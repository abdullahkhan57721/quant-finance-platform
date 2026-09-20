"""Two independent valuation methods over one explicitly composed Heston problem."""

from datetime import date

from qf_platform.application import (
    HestonPricingAnalysis,
    HestonPricingRequest,
    run_heston_pricing,
)
from qf_platform.pricing import (
    EuropeanOption,
    FlatMoneyMarketNumeraire,
    HestonEquityState,
    HestonFourierEuropeanOption,
    HestonLaw,
    HestonMonteCarloEuropeanOption,
    HestonParameters,
    ModeledState,
    OptionRight,
    PricingMeasureSemantics,
    PricingProblem,
)


def make_request() -> HestonPricingRequest:
    valuation_date = date(2026, 1, 1)
    law = HestonLaw()
    numeraire = FlatMoneyMarketNumeraire(valuation_date, 0.03)
    problem = PricingProblem(
        current_state=ModeledState(
            valuation_date, HestonEquityState(100.0, 0.04), law.state_space
        ),
        stochastic_law=law,
        parameters=HestonParameters(
            mean_reversion_speed=2.0,
            long_run_variance=0.04,
            volatility_of_variance=0.5,
            correlation=-0.7,
            continuous_dividend_yield=0.01,
        ),
        contract=EuropeanOption(date(2027, 1, 1), 100.0, OptionRight.CALL),
        numeraire=numeraire,
        pricing_measure=PricingMeasureSemantics(name="Q^B", numeraire=numeraire),
    )
    return HestonPricingRequest(
        problem=problem,
        fourier_method=HestonFourierEuropeanOption(
            integration_lower_bound=1e-8, integration_upper_bound=80.0, intervals=256
        ),
        monte_carlo_method=HestonMonteCarloEuropeanOption(
            paths=4000, time_steps=128, seed=1729
        ),
    )


def run_example() -> HestonPricingAnalysis:
    return run_heston_pricing(make_request())


if __name__ == "__main__":
    analysis = run_example()
    print("Fourier:", analysis.fourier_result)
    print("Monte Carlo:", analysis.monte_carlo_result)
    print("Fourier resolution evidence:", analysis.fourier_stability)
    print("MC sampling interval excludes timestep bias and model error.")
