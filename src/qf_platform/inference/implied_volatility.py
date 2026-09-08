"""Black-Scholes implied volatility as M4's first concrete inverse problem."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from math import exp, isfinite, log
from typing import Protocol, cast

from qf_platform._validation import finite_real
from qf_platform.market_data.normalization import NormalizedOptionObservation
from qf_platform.pricing.black_scholes import BlackScholesLaw, BlackScholesParameters
from qf_platform.pricing.black_scholes_valuation import BlackScholesClosedForm
from qf_platform.pricing.dates import actual_365_fixed_year_fraction
from qf_platform.pricing.equity import EquityState, EuropeanOption, OptionRight
from qf_platform.pricing.measures import (
    PricingMeasureSemantics,
    validated_numeraire_value,
)
from qf_platform.pricing.numeraire import FlatMoneyMarketNumeraire
from qf_platform.pricing.problem import PricingProblem
from qf_platform.pricing.state import ModeledState
from qf_platform.pricing.valuation import evaluate
from qf_platform.sensitivity import (
    AnalyticBlackScholesSensitivity,
    BlackScholesSensitivity,
    BlackScholesSensitivityProblem,
    evaluate_sensitivity,
)

_PRICE_BOUND_RELATIVE_TOLERANCE = 1.0e-12


class InvalidImpliedVolatilityProblem(ValueError):
    """Raised when the financial inverse problem is not identifiable as configured."""


class InconsistentObservedPrice(InvalidImpliedVolatilityProblem):
    """Raised when an observed target violates European option price bounds."""


class ImpliedVolatilityNotBracketed(ValueError):
    """Raised when the admissible volatility domain does not bracket a solution."""


class ImpliedVolatilityConvergenceError(RuntimeError):
    """Raised when a bracketed numerical solve remains unresolved."""


@dataclass(frozen=True, slots=True)
class OptionPriceBounds:
    """Discounted European option lower/upper bounds at one valuation date."""

    lower: float
    upper: float

    def __post_init__(self) -> None:
        lower = finite_real(self.lower, name="lower price bound")
        upper = finite_real(self.upper, name="upper price bound")
        if lower < 0.0:
            msg = "lower price bound must be non-negative"
            raise ValueError(msg)
        if upper < lower:
            msg = "upper price bound must not be below lower price bound"
            raise ValueError(msg)
        object.__setattr__(self, "lower", lower)
        object.__setattr__(self, "upper", upper)


def _price_bound_tolerance(bounds: OptionPriceBounds, target: float) -> float:
    scale = max(1.0, abs(bounds.lower), abs(bounds.upper), abs(target))
    return _PRICE_BOUND_RELATIVE_TOLERANCE * scale


@dataclass(frozen=True, slots=True)
class BlackScholesImpliedVolatilityProblem:
    """Financial statement of one Black-Scholes implied-volatility inverse problem.

    The observed target remains attached to ``observation``. This object supplies the
    Black-Scholes model context and admissible volatility domain; it does not choose a
    root-finding algorithm.
    """

    observation: NormalizedOptionObservation
    numeraire: FlatMoneyMarketNumeraire
    pricing_measure: PricingMeasureSemantics[date]
    continuous_dividend_yield: float = 0.0
    minimum_annualized_volatility: float = 0.0
    maximum_annualized_volatility: float = 5.0

    def __post_init__(self) -> None:
        if not isinstance(cast(object, self.observation), NormalizedOptionObservation):
            msg = "observation must be a NormalizedOptionObservation"
            raise TypeError(msg)
        if not isinstance(cast(object, self.numeraire), FlatMoneyMarketNumeraire):
            msg = "numeraire must be a FlatMoneyMarketNumeraire"
            raise TypeError(msg)
        if not isinstance(cast(object, self.pricing_measure), PricingMeasureSemantics):
            msg = "pricing_measure must be PricingMeasureSemantics"
            raise TypeError(msg)
        if self.pricing_measure.numeraire is not self.numeraire:
            msg = "pricing_measure must reference the problem numeraire"
            raise InvalidImpliedVolatilityProblem(msg)

        dividend_yield = finite_real(
            self.continuous_dividend_yield,
            name="continuous_dividend_yield",
        )
        minimum = finite_real(
            self.minimum_annualized_volatility,
            name="minimum_annualized_volatility",
        )
        maximum = finite_real(
            self.maximum_annualized_volatility,
            name="maximum_annualized_volatility",
        )
        if minimum < 0.0:
            msg = "minimum_annualized_volatility must be non-negative"
            raise InvalidImpliedVolatilityProblem(msg)
        if maximum <= minimum:
            msg = "maximum_annualized_volatility must exceed the minimum"
            raise InvalidImpliedVolatilityProblem(msg)
        object.__setattr__(self, "continuous_dividend_yield", dividend_yield)
        object.__setattr__(self, "minimum_annualized_volatility", minimum)
        object.__setattr__(self, "maximum_annualized_volatility", maximum)

        quote = self.observation.raw_quote
        if quote.expiry <= self.observation.valuation_date:
            msg = "implied volatility requires strictly positive time to expiry"
            raise InvalidImpliedVolatilityProblem(msg)
        if quote.strike <= 0.0:
            msg = "implied volatility requires a strictly positive strike"
            raise InvalidImpliedVolatilityProblem(msg)

        bounds = self.price_bounds
        target = self.observation.target_price
        tolerance = _price_bound_tolerance(bounds, target)
        if target < bounds.lower - tolerance or target > bounds.upper + tolerance:
            msg = (
                f"observed target {target} is outside European option price bounds "
                f"[{bounds.lower}, {bounds.upper}]"
            )
            raise InconsistentObservedPrice(msg)

    @property
    def contract(self) -> EuropeanOption:
        """Return the European payoff semantics carried by the observation."""

        quote = self.observation.raw_quote
        return EuropeanOption(
            expiry=quote.expiry, strike=quote.strike, right=quote.right
        )

    @property
    def year_fraction(self) -> float:
        """Return M1's ACT/365F time to expiry."""

        return actual_365_fixed_year_fraction(
            self.observation.valuation_date,
            self.observation.raw_quote.expiry,
        )

    @property
    def price_bounds(self) -> OptionPriceBounds:
        """Return no-arbitrage bounds before any numerical root search begins."""

        valuation_date = self.observation.valuation_date
        expiry = self.observation.raw_quote.expiry
        numeraire_now = validated_numeraire_value(self.numeraire, valuation_date)
        numeraire_expiry = validated_numeraire_value(self.numeraire, expiry)
        risk_free_discount = numeraire_now / numeraire_expiry
        try:
            dividend_discount = exp(
                -self.continuous_dividend_yield * self.year_fraction
            )
        except OverflowError as exc:
            msg = "dividend discount factor must be positive and finite"
            raise InvalidImpliedVolatilityProblem(msg) from exc
        if not isfinite(dividend_discount) or dividend_discount <= 0.0:
            msg = "dividend discount factor must be positive and finite"
            raise InvalidImpliedVolatilityProblem(msg)

        discounted_spot = self.observation.spot * dividend_discount
        discounted_strike = self.observation.raw_quote.strike * risk_free_discount
        if self.observation.raw_quote.right is OptionRight.CALL:
            return OptionPriceBounds(
                lower=max(discounted_spot - discounted_strike, 0.0),
                upper=discounted_spot,
            )
        return OptionPriceBounds(
            lower=max(discounted_strike - discounted_spot, 0.0),
            upper=discounted_strike,
        )


@dataclass(frozen=True, slots=True)
class ImpliedVolatilityResult:
    """Completed implied-volatility inference with numerical/conditioning evidence."""

    observation: NormalizedOptionObservation
    annualized_volatility: float
    model_price: float
    residual: float
    iterations: int
    function_evaluations: int
    vega: float | None
    volatility_change_per_price_unit: float | None
    local_volatility_shift_for_half_spread: float | None

    def __post_init__(self) -> None:
        if not isinstance(cast(object, self.observation), NormalizedOptionObservation):
            msg = "observation must be a NormalizedOptionObservation"
            raise TypeError(msg)
        for name in ("annualized_volatility", "model_price", "residual"):
            object.__setattr__(
                self,
                name,
                finite_real(getattr(self, name), name=name),
            )
        if self.annualized_volatility < 0.0:
            msg = "annualized_volatility must be non-negative"
            raise ValueError(msg)
        for name in ("iterations", "function_evaluations"):
            value = getattr(self, name)
            if type(value) is not int:
                msg = f"{name} must be an integer"
                raise TypeError(msg)
            if value < 0:
                msg = f"{name} must be non-negative"
                raise ValueError(msg)
        for name in (
            "vega",
            "volatility_change_per_price_unit",
            "local_volatility_shift_for_half_spread",
        ):
            value = getattr(self, name)
            if value is not None:
                object.__setattr__(self, name, finite_real(value, name=name))

    @property
    def target_price(self) -> float:
        """Return the normalized observed value being inverted."""

        return self.observation.target_price

    @property
    def moneyness(self) -> float:
        """Return strike divided by observed spot."""

        return self.observation.raw_quote.strike / self.observation.spot


class BlackScholesImpliedVolatilityMethod(Protocol):
    """Numerical-method responsibility for this concrete inverse-problem family."""

    def solve(
        self,
        problem: BlackScholesImpliedVolatilityProblem,
        /,
    ) -> ImpliedVolatilityResult:
        """Solve one already-formed Black-Scholes implied-volatility problem."""
        ...


def _pricing_problem(
    problem: BlackScholesImpliedVolatilityProblem,
    annualized_volatility: float,
) -> PricingProblem[date, EquityState, BlackScholesParameters]:
    law = BlackScholesLaw()
    state = ModeledState(
        time=problem.observation.valuation_date,
        value=EquityState(problem.observation.spot),
        state_space=law.state_space,
    )
    return PricingProblem(
        current_state=state,
        stochastic_law=law,
        parameters=BlackScholesParameters(
            annualized_volatility=annualized_volatility,
            continuous_dividend_yield=problem.continuous_dividend_yield,
        ),
        contract=problem.contract,
        numeraire=problem.numeraire,
        pricing_measure=problem.pricing_measure,
    )


def _price(
    problem: BlackScholesImpliedVolatilityProblem,
    annualized_volatility: float,
) -> float:
    return evaluate(
        _pricing_problem(problem, annualized_volatility),
        BlackScholesClosedForm(),
    ).present_value


def _conditioning_vega(
    problem: BlackScholesImpliedVolatilityProblem,
    annualized_volatility: float,
) -> float | None:
    if annualized_volatility <= 0.0:
        return None
    sensitivity_problem = BlackScholesSensitivityProblem(
        pricing_problem=_pricing_problem(problem, annualized_volatility),
        sensitivity=BlackScholesSensitivity.VEGA,
    )
    return evaluate_sensitivity(
        sensitivity_problem,
        AnalyticBlackScholesSensitivity(),
    ).value


def _completed_result(
    problem: BlackScholesImpliedVolatilityProblem,
    *,
    annualized_volatility: float,
    model_price: float,
    iterations: int,
    function_evaluations: int,
) -> ImpliedVolatilityResult:
    residual = model_price - problem.observation.target_price
    vega = _conditioning_vega(problem, annualized_volatility)
    volatility_per_price_unit: float | None = None
    half_spread_shift: float | None = None
    if vega is not None and vega > 0.0:
        inverse_vega = 1.0 / vega
        if isfinite(inverse_vega):
            volatility_per_price_unit = inverse_vega
            bid = problem.observation.raw_quote.bid
            ask = problem.observation.raw_quote.ask
            if bid is not None and ask is not None:
                shift = 0.5 * (ask - bid) * inverse_vega
                if isfinite(shift):
                    half_spread_shift = shift
    return ImpliedVolatilityResult(
        observation=problem.observation,
        annualized_volatility=annualized_volatility,
        model_price=model_price,
        residual=residual,
        iterations=iterations,
        function_evaluations=function_evaluations,
        vega=vega,
        volatility_change_per_price_unit=volatility_per_price_unit,
        local_volatility_shift_for_half_spread=half_spread_shift,
    )


@dataclass(frozen=True, slots=True)
class BisectionImpliedVolatility:
    """Deterministic bracketed solve for monotone Black-Scholes price in volatility."""

    price_tolerance: float = 1.0e-10
    volatility_tolerance: float = 1.0e-10
    max_iterations: int = 200

    def __post_init__(self) -> None:
        for name in ("price_tolerance", "volatility_tolerance"):
            value = finite_real(getattr(self, name), name=name)
            if value <= 0.0:
                msg = f"{name} must be positive"
                raise ValueError(msg)
            object.__setattr__(self, name, value)
        if type(self.max_iterations) is not int:
            msg = "max_iterations must be an integer"
            raise TypeError(msg)
        if self.max_iterations <= 0:
            msg = "max_iterations must be positive"
            raise ValueError(msg)

    def solve(
        self,
        problem: BlackScholesImpliedVolatilityProblem,
        /,
    ) -> ImpliedVolatilityResult:
        """Bracket then bisect, refusing unresolved or out-of-domain targets."""

        lower_volatility = problem.minimum_annualized_volatility
        upper_volatility = problem.maximum_annualized_volatility
        target = problem.observation.target_price
        lower_price = _price(problem, lower_volatility)
        upper_price = _price(problem, upper_volatility)
        function_evaluations = 2

        if abs(lower_price - target) <= self.price_tolerance:
            return _completed_result(
                problem,
                annualized_volatility=lower_volatility,
                model_price=lower_price,
                iterations=0,
                function_evaluations=function_evaluations,
            )
        if abs(upper_price - target) <= self.price_tolerance:
            return _completed_result(
                problem,
                annualized_volatility=upper_volatility,
                model_price=upper_price,
                iterations=0,
                function_evaluations=function_evaluations,
            )
        if target < lower_price or target > upper_price:
            msg = (
                f"observed target {target} is not bracketed by model prices "
                f"[{lower_price}, {upper_price}] on volatility domain "
                f"[{lower_volatility}, {upper_volatility}]"
            )
            raise ImpliedVolatilityNotBracketed(msg)

        for iteration in range(1, self.max_iterations + 1):
            midpoint_volatility = 0.5 * (lower_volatility + upper_volatility)
            midpoint_price = _price(problem, midpoint_volatility)
            function_evaluations += 1
            residual = midpoint_price - target
            if abs(residual) <= self.price_tolerance:
                return _completed_result(
                    problem,
                    annualized_volatility=midpoint_volatility,
                    model_price=midpoint_price,
                    iterations=iteration,
                    function_evaluations=function_evaluations,
                )

            if residual < 0.0:
                lower_volatility = midpoint_volatility
            else:
                upper_volatility = midpoint_volatility

            if upper_volatility - lower_volatility <= self.volatility_tolerance:
                final_volatility = 0.5 * (lower_volatility + upper_volatility)
                final_price = _price(problem, final_volatility)
                function_evaluations += 1
                return _completed_result(
                    problem,
                    annualized_volatility=final_volatility,
                    model_price=final_price,
                    iterations=iteration,
                    function_evaluations=function_evaluations,
                )

        msg = "implied-volatility bisection exceeded max_iterations"
        raise ImpliedVolatilityConvergenceError(msg)


def infer_implied_volatility(
    problem: BlackScholesImpliedVolatilityProblem,
    method: BlackScholesImpliedVolatilityMethod,
    /,
) -> ImpliedVolatilityResult:
    """Apply a numerical method to one concrete financial inverse problem."""

    return method.solve(problem)


def log_forward_moneyness(problem: BlackScholesImpliedVolatilityProblem) -> float:
    """Return log(K/F) under the forward map's flat-rate/carry convention."""

    rate = problem.numeraire.continuously_compounded_rate
    forward = problem.observation.spot * exp(
        (rate - problem.continuous_dividend_yield) * problem.year_fraction
    )
    if not isfinite(forward) or forward <= 0.0:
        msg = "forward level must be positive and finite"
        raise InvalidImpliedVolatilityProblem(msg)
    return log(problem.observation.raw_quote.strike / forward)
