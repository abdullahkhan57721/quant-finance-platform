"""Thin web-service composition over authoritative application/presentation APIs."""

from __future__ import annotations

from dataclasses import dataclass

from qf_platform.application import (
    BlackScholesStudyDraft,
    HedgeWorkbenchDraft,
    HestonCalibrationDraft,
    HestonPricingDraft,
    M2WorkbenchDraft,
    canonical_m4_market_workbench,
    canonical_m6_market_reference,
    canonical_m8_performance_reference,
    compose_black_scholes_study,
    make_hedge_workbench_request,
    make_heston_calibration_request,
    make_heston_pricing_request,
    make_m2_workbench_request,
    make_ui5_reference_validation_request,
    run_hedge_workbench,
    run_heston_calibration,
    run_heston_pricing,
    run_m2_workbench,
    run_ui5_validation,
)
from qf_platform.presentation import (
    HedgeWorkbenchPresentation,
    HestonCalibrationPresentation,
    HestonPricingPresentation,
    M2WorkbenchPresentation,
    M6MarketReferencePresentation,
    MarketWorkbenchPresentation,
    UI5PerformancePresentation,
    UI5ValidationPresentation,
    build_hedge_workbench_presentation,
    build_heston_calibration_presentation,
    build_heston_pricing_presentation,
    build_m2_workbench_presentation,
    build_m6_market_reference_presentation,
    build_market_workbench_presentation,
    build_ui5_performance_presentation,
    build_ui5_validation_presentation,
)


@dataclass(frozen=True, slots=True)
class ServiceResult[T]:
    """One explicit web-service outcome; failures are never converted to zeros."""

    value: T | None = None
    error: str | None = None

    def __post_init__(self) -> None:
        if (self.value is None) == (self.error is None):
            raise ValueError("service result requires exactly one of value or error")


@dataclass(frozen=True, slots=True)
class ValuationInputs:
    """Transient browser text for the M1/M2 pricing and sensitivity workflow."""

    spot: str = "100"
    strike: str = "100"
    valuation_date: str = "2026-01-01"
    expiry: str = "2027-01-01"
    annualized_volatility: str = "0.20"
    continuously_compounded_rate: str = "0.05"
    continuous_dividend_yield: str = "0.00"
    option_right: str = "call"
    valuation_method: str = "analytic"
    crr_steps: str = "400"
    monte_carlo_paths: str = "20000"
    monte_carlo_seed: str = "1729"
    selected_greek: str = "delta"


@dataclass(frozen=True, slots=True)
class HedgingInputs:
    """Transient browser text for the concrete M3 replication experiment."""

    spot: str = "100"
    strike: str = "100"
    valuation_date: str = "2026-01-01"
    expiry: str = "2027-01-01"
    option_right: str = "call"
    generating_volatility: str = "0.20"
    hedging_volatility: str = "0.20"
    rebalance_day_interval: str = "7"
    seed: str = "1729"
    replicate_count: str = "16"
    transaction_cost_rate: str = "0.0"


def run_valuation_service(
    inputs: ValuationInputs | None = None,
) -> ServiceResult[M2WorkbenchPresentation]:
    """Run M2 through existing Draft/request/application/presentation contracts."""

    inputs = inputs or ValuationInputs()
    try:
        composition = compose_black_scholes_study(
            BlackScholesStudyDraft(
                spot=inputs.spot,
                strike=inputs.strike,
                valuation_date=inputs.valuation_date,
                expiry=inputs.expiry,
                annualized_volatility=inputs.annualized_volatility,
                continuously_compounded_rate=inputs.continuously_compounded_rate,
                continuous_dividend_yield=inputs.continuous_dividend_yield,
                option_right=inputs.option_right,
            )
        )
        request = make_m2_workbench_request(
            composition,
            M2WorkbenchDraft(
                valuation_method=inputs.valuation_method,
                crr_steps=inputs.crr_steps,
                monte_carlo_paths=inputs.monte_carlo_paths,
                monte_carlo_seed=inputs.monte_carlo_seed,
                selected_greek=inputs.selected_greek,
            ),
        )
        analysis = run_m2_workbench(request)
        return ServiceResult(
            value=build_m2_workbench_presentation(request, analysis),
        )
    except (ValueError, TypeError, RuntimeError) as exc:
        return ServiceResult(error=str(exc))


def run_hedging_service(
    inputs: HedgingInputs | None = None,
) -> ServiceResult[HedgeWorkbenchPresentation]:
    """Run M3 through the existing hedge workbench; browser code owns no accounting."""

    inputs = inputs or HedgingInputs()
    try:
        composition = compose_black_scholes_study(
            BlackScholesStudyDraft(
                spot=inputs.spot,
                strike=inputs.strike,
                valuation_date=inputs.valuation_date,
                expiry=inputs.expiry,
                annualized_volatility=inputs.hedging_volatility,
                continuously_compounded_rate="0.05",
                continuous_dividend_yield="0.00",
                option_right=inputs.option_right,
            )
        )
        request = make_hedge_workbench_request(
            composition,
            HedgeWorkbenchDraft(
                generating_volatility=inputs.generating_volatility,
                hedging_volatility=inputs.hedging_volatility,
                rebalance_day_interval=inputs.rebalance_day_interval,
                seed=inputs.seed,
                replicate_count=inputs.replicate_count,
                transaction_cost_rate=inputs.transaction_cost_rate,
            ),
        )
        analysis = run_hedge_workbench(request)
        return ServiceResult(
            value=build_hedge_workbench_presentation(request, analysis),
        )
    except (ValueError, TypeError, RuntimeError) as exc:
        return ServiceResult(error=str(exc))


def load_market_service() -> ServiceResult[MarketWorkbenchPresentation]:
    """Load package-safe M4 synthetic + derived empirical evidence without network I/O."""

    try:
        return ServiceResult(
            value=build_market_workbench_presentation(canonical_m4_market_workbench()),
        )
    except (ValueError, TypeError, RuntimeError) as exc:
        return ServiceResult(error=str(exc))


def run_heston_pricing_service(
    draft: HestonPricingDraft | None = None,
) -> ServiceResult[HestonPricingPresentation]:
    """Run the existing M5 independent Heston valuation study."""

    try:
        request = make_heston_pricing_request(draft or HestonPricingDraft())
        analysis = run_heston_pricing(request)
        return ServiceResult(
            value=build_heston_pricing_presentation(request, analysis),
        )
    except (ValueError, TypeError, RuntimeError) as exc:
        return ServiceResult(error=str(exc))


def run_heston_calibration_service(
    mode: str = "recovery",
    draft: HestonCalibrationDraft | None = None,
) -> ServiceResult[HestonCalibrationPresentation]:
    """Run the existing M6 synthetic recovery/non-identifiability workbench."""

    try:
        request = make_heston_calibration_request(
            mode,
            draft or HestonCalibrationDraft(),
        )
        analysis = run_heston_calibration(request)
        return ServiceResult(
            value=build_heston_calibration_presentation(analysis),
        )
    except (ValueError, TypeError, RuntimeError) as exc:
        return ServiceResult(error=str(exc))


def load_m6_market_reference_service() -> ServiceResult[M6MarketReferencePresentation]:
    """Render recorded M6 empirical calibration evidence without recalibrating."""

    try:
        return ServiceResult(
            value=build_m6_market_reference_presentation(
                canonical_m6_market_reference()
            ),
        )
    except (ValueError, TypeError, RuntimeError) as exc:
        return ServiceResult(error=str(exc))


def load_validation_service() -> ServiceResult[UI5ValidationPresentation]:
    """Recompute the package-safe M7 reference validation through production APIs."""

    try:
        request = make_ui5_reference_validation_request()
        analysis = run_ui5_validation(request)
        return ServiceResult(
            value=build_ui5_validation_presentation(analysis),
        )
    except (ValueError, TypeError, RuntimeError) as exc:
        return ServiceResult(error=str(exc))


def load_performance_service() -> ServiceResult[UI5PerformancePresentation]:
    """Render revision-pinned M8 evidence; this does not benchmark the current run."""

    try:
        return ServiceResult(
            value=build_ui5_performance_presentation(
                canonical_m8_performance_reference()
            ),
        )
    except (ValueError, TypeError, RuntimeError) as exc:
        return ServiceResult(error=str(exc))
