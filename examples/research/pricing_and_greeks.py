"""Compare M1/M2 methods and Greeks using numeric inputs and public contracts."""

from datetime import date

from qf_platform.application import (
    BlackScholesStudyComposition,
    M2WorkbenchAnalysis,
    M2WorkbenchConfig,
    M2WorkbenchRequest,
    WorkbenchValuationMethod,
    run_m2_workbench,
)
from qf_platform.pricing import (
    BlackScholesClosedForm,
    BlackScholesLaw,
    BlackScholesParameters,
    EquityState,
    EuropeanOption,
    FlatMoneyMarketNumeraire,
    ModeledState,
    OptionRight,
    PricingMeasureSemantics,
    PricingProblem,
)
from qf_platform.sensitivity import (
    BlackScholesSensitivity,
    FiniteDifferenceBlackScholesSensitivity,
)


def make_request() -> M2WorkbenchRequest:
    """One-year ATM call; rates/volatility in decimals, ACT/365F dates."""
    valuation_date = date(2026, 1, 1)
    law = BlackScholesLaw()
    numeraire = FlatMoneyMarketNumeraire(valuation_date, 0.05)
    problem = PricingProblem(
        current_state=ModeledState(valuation_date, EquityState(100.0), law.state_space),
        stochastic_law=law,
        parameters=BlackScholesParameters(annualized_volatility=0.20),
        contract=EuropeanOption(date(2027, 1, 1), 100.0, OptionRight.CALL),
        numeraire=numeraire,
        pricing_measure=PricingMeasureSemantics(name="Q^B", numeraire=numeraire),
    )
    return M2WorkbenchRequest(
        composition=BlackScholesStudyComposition(problem, BlackScholesClosedForm()),
        config=M2WorkbenchConfig(
            valuation_method=WorkbenchValuationMethod.ANALYTIC,
            crr_steps=400,
            monte_carlo_paths=20_000,
            monte_carlo_seed=1729,
            selected_greek=BlackScholesSensitivity.DELTA,
            finite_difference_method=FiniteDifferenceBlackScholesSensitivity(
                spot_bump=0.1,
                volatility_bump=0.001,
                rate_bump=0.0001,
                theta_day_bump=1,
            ),
        ),
    )


def run_example() -> M2WorkbenchAnalysis:
    return run_m2_workbench(make_request())


if __name__ == "__main__":
    analysis = run_example()
    for run in analysis.valuations:
        print(run.method.value, run.configuration, run.result)
    for greek in analysis.sensitivities:
        result = greek.analytic_result
        if result is not None:
            print(result.sensitivity.value, result.value, result.units)
    print("MC intervals cover sampling uncertainty, not model error.")
