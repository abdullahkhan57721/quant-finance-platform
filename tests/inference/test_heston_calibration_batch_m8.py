from __future__ import annotations

from datetime import date

import numpy as np
import pytest

from qf_platform.inference.heston_calibration import (
    HestonCalibrationBounds,
    HestonCalibrationCoordinates,
    HestonCalibrationProblem,
    HestonCalibrationWeighting,
    HestonPriceCalibrationTarget,
    evaluate_heston_calibration_residuals,
)
from qf_platform.inference.heston_calibration_batch import (
    evaluate_heston_calibration_standardized_residual_vector_batched,
)
from qf_platform.pricing import (
    EuropeanOption,
    FlatMoneyMarketNumeraire,
    HestonEquityState,
    HestonFourierEuropeanOption,
    HestonLaw,
    ModeledState,
    OptionRight,
    PricingMeasureSemantics,
    PricingProblem,
    evaluate,
)

_VALUATION_DATE = date(2026, 1, 1)
_Q = 0.01
_TRUE = HestonCalibrationCoordinates.from_vector(
    (0.04, 2.0, 0.04, 0.5, -0.7),
    continuous_dividend_yield=_Q,
)
_EVALUATED = HestonCalibrationCoordinates.from_vector(
    (0.055, 1.6, 0.05, 0.65, -0.55),
    continuous_dividend_yield=_Q,
)


def _price(contract: EuropeanOption) -> float:
    law = HestonLaw()
    numeraire = FlatMoneyMarketNumeraire(
        reference_date=_VALUATION_DATE,
        continuously_compounded_rate=0.03,
    )
    problem = PricingProblem(
        current_state=ModeledState(
            time=_VALUATION_DATE,
            value=HestonEquityState(
                spot=100.0,
                instantaneous_variance=_TRUE.initial_variance,
            ),
            state_space=law.state_space,
        ),
        stochastic_law=law,
        parameters=_TRUE.parameters,
        contract=contract,
        numeraire=numeraire,
        pricing_measure=PricingMeasureSemantics(name="Q^N", numeraire=numeraire),
    )
    return evaluate(
        problem,
        HestonFourierEuropeanOption(
            integration_upper_bound=100.0,
            intervals=256,
        ),
    ).present_value


def _problem() -> HestonCalibrationProblem:
    contracts = (
        EuropeanOption(date(2026, 7, 1), 85.0, OptionRight.PUT),
        EuropeanOption(date(2026, 7, 1), 100.0, OptionRight.CALL),
        EuropeanOption(date(2026, 7, 1), 115.0, OptionRight.CALL),
        EuropeanOption(date(2027, 1, 1), 90.0, OptionRight.PUT),
        EuropeanOption(date(2027, 1, 1), 110.0, OptionRight.CALL),
    )
    targets = tuple(
        HestonPriceCalibrationTarget.synthetic(
            contract=contract,
            target_price=_price(contract),
            label=f"target-{index}",
        )
        for index, contract in enumerate(contracts)
    )
    numeraire = FlatMoneyMarketNumeraire(
        reference_date=_VALUATION_DATE,
        continuously_compounded_rate=0.03,
    )
    return HestonCalibrationProblem(
        valuation_date=_VALUATION_DATE,
        spot=100.0,
        targets=targets,
        numeraire=numeraire,
        pricing_measure=PricingMeasureSemantics(name="Q^N", numeraire=numeraire),
        continuous_dividend_yield=_Q,
        bounds=HestonCalibrationBounds(),
        weighting=HestonCalibrationWeighting.UNIFORM_PRICE,
        forward_method=HestonFourierEuropeanOption(
            integration_upper_bound=100.0,
            intervals=256,
        ),
    )


def _scalar_standardized_residuals(
    problem: HestonCalibrationProblem,
    coordinates: HestonCalibrationCoordinates,
) -> np.ndarray:
    return np.asarray(
        [
            item.standardized_residual
            for item in evaluate_heston_calibration_residuals(problem, coordinates)
        ],
        dtype=np.float64,
    )


def test_batched_calibration_residual_vector_matches_scalar_reference() -> None:
    problem = _problem()
    scalar = _scalar_standardized_residuals(problem, _EVALUATED)
    batched = evaluate_heston_calibration_standardized_residual_vector_batched(
        problem,
        _EVALUATED,
    )

    assert batched == pytest.approx(scalar, abs=2.0e-11)


def test_batched_calibration_preserves_xi_zero_reference_boundary() -> None:
    problem = _problem()
    deterministic_variance = HestonCalibrationCoordinates.from_vector(
        (0.055, 1.6, 0.05, 0.0, -0.55),
        continuous_dividend_yield=_Q,
    )

    scalar = _scalar_standardized_residuals(problem, deterministic_variance)
    batched = evaluate_heston_calibration_standardized_residual_vector_batched(
        problem,
        deterministic_variance,
    )

    assert batched == pytest.approx(scalar, abs=1.0e-12)
