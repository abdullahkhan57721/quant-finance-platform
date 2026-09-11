"""Measured M8 optimization for Heston calibration residual evaluation.

The public scalar residual evaluator remains the readable correctness/reference path.
This module supplies only the optimizer's repeated numeric residual vector, batching the
already-defined M6 pricing questions by expiry through the measured Heston Fourier
batch kernel.
"""

from __future__ import annotations

from datetime import date

import numpy as np
from numpy.typing import NDArray

from qf_platform.inference.heston_calibration import (
    HestonCalibrationCoordinates,
    HestonCalibrationProblem,
    InvalidHestonCalibrationProblem,
)
from qf_platform.pricing.heston import HestonEquityState, HestonLaw, HestonParameters
from qf_platform.pricing.heston_fourier_batch import batch_heston_fourier_present_values
from qf_platform.pricing.problem import PricingProblem
from qf_platform.pricing.state import ModeledState


def evaluate_heston_calibration_standardized_residual_vector_batched(
    problem: HestonCalibrationProblem,
    coordinates: HestonCalibrationCoordinates,
    /,
) -> NDArray[np.float64]:
    """Evaluate the M6 standardized residual vector with stateless batch pricing."""

    if (
        coordinates.parameters.continuous_dividend_yield
        != problem.continuous_dividend_yield
    ):
        msg = "calibration coordinates must use the problem's fixed dividend yield"
        raise InvalidHestonCalibrationProblem(msg)

    law = HestonLaw()
    pricing_problems: list[
        PricingProblem[date, HestonEquityState, HestonParameters]
    ] = []
    for target in problem.targets:
        pricing_problems.append(
            PricingProblem(
                current_state=ModeledState(
                    time=problem.valuation_date,
                    value=HestonEquityState(
                        spot=problem.spot,
                        instantaneous_variance=coordinates.initial_variance,
                    ),
                    state_space=law.state_space,
                ),
                stochastic_law=law,
                parameters=coordinates.parameters,
                contract=target.contract,
                numeraire=problem.numeraire,
                pricing_measure=problem.pricing_measure,
            )
        )

    model_prices = batch_heston_fourier_present_values(
        tuple(pricing_problems),
        problem.forward_method,
    )
    return np.asarray(
        [
            (model_price - target.target_price) / problem.residual_scale(target)
            for model_price, target in zip(model_prices, problem.targets, strict=True)
        ],
        dtype=np.float64,
    )
