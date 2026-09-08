"""SciPy nonlinear least-squares method for the concrete M6 Heston inverse problem."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from sys import float_info
from typing import cast

import numpy as np
from numpy.typing import NDArray
from scipy.linalg import svdvals
from scipy.optimize import least_squares

from qf_platform._validation import finite_real
from qf_platform.inference.heston_calibration import (
    HestonCalibrationConditioning,
    HestonCalibrationConvergenceError,
    HestonCalibrationCoordinates,
    HestonCalibrationProblem,
    HestonCalibrationResult,
    InvalidHestonCalibrationInitialGuess,
    evaluate_heston_calibration_residuals,
)


@dataclass(frozen=True, slots=True)
class ScipyLeastSquaresHestonCalibration:
    """Bound-constrained trust-region least squares in direct financial coordinates.

    The financial problem supplies residual semantics, weighting, admissible bounds, and
    the M5 forward-pricing dependency. This method supplies only numerical search
    configuration. No parameter transform is used: optimizer coordinates are exactly
    ``(v0, kappa, theta, xi, rho)`` in their financial units.
    """

    initial_guess: HestonCalibrationCoordinates
    function_tolerance: float = 1.0e-10
    coordinate_tolerance: float = 1.0e-10
    gradient_tolerance: float = 1.0e-10
    max_function_evaluations: int = 300

    def __post_init__(self) -> None:
        if not isinstance(cast(object, self.initial_guess), HestonCalibrationCoordinates):
            msg = "initial_guess must be HestonCalibrationCoordinates"
            raise TypeError(msg)
        for name in (
            "function_tolerance",
            "coordinate_tolerance",
            "gradient_tolerance",
        ):
            value = finite_real(getattr(self, name), name=name)
            if value <= 0.0:
                msg = f"{name} must be strictly positive"
                raise ValueError(msg)
            object.__setattr__(self, name, value)
        if type(self.max_function_evaluations) is not int:
            msg = "max_function_evaluations must be an integer"
            raise TypeError(msg)
        if self.max_function_evaluations <= 0:
            msg = "max_function_evaluations must be strictly positive"
            raise ValueError(msg)

    def solve(self, problem: HestonCalibrationProblem, /) -> HestonCalibrationResult:
        """Calibrate one already-formed financial inverse problem."""

        self._validate_initial_guess(problem)
        lower = np.asarray(problem.bounds.lower_vector, dtype=np.float64)
        upper = np.asarray(problem.bounds.upper_vector, dtype=np.float64)
        initial = np.asarray(self.initial_guess.as_vector(), dtype=np.float64)

        def residual_vector(values: NDArray[np.float64]) -> NDArray[np.float64]:
            coordinates = HestonCalibrationCoordinates.from_vector(
                _financial_vector(values),
                continuous_dividend_yield=problem.continuous_dividend_yield,
            )
            residuals = evaluate_heston_calibration_residuals(problem, coordinates)
            return np.asarray(
                [item.standardized_residual for item in residuals],
                dtype=np.float64,
            )

        optimizer_result = least_squares(
            residual_vector,
            initial,
            bounds=(lower, upper),
            method="trf",
            jac="2-point",
            x_scale="jac",
            ftol=self.function_tolerance,
            xtol=self.coordinate_tolerance,
            gtol=self.gradient_tolerance,
            max_nfev=self.max_function_evaluations,
        )
        success = cast(bool, optimizer_result.success)
        status = int(cast(int, optimizer_result.status))
        message = str(optimizer_result.message)
        function_evaluations = int(cast(int, optimizer_result.nfev))
        jacobian_evaluations_raw = cast(int | None, optimizer_result.njev)
        jacobian_evaluations = (
            0 if jacobian_evaluations_raw is None else int(jacobian_evaluations_raw)
        )
        if not success:
            msg = (
                "Heston calibration optimizer did not converge: "
                f"status={status}, nfev={function_evaluations}, message={message}"
            )
            raise HestonCalibrationConvergenceError(msg)

        solution = cast(NDArray[np.float64], optimizer_result.x)
        estimate = HestonCalibrationCoordinates.from_vector(
            _financial_vector(solution),
            continuous_dividend_yield=problem.continuous_dividend_yield,
        )
        residuals = evaluate_heston_calibration_residuals(problem, estimate)
        objective_value = sum(item.standardized_residual**2 for item in residuals)
        jacobian = cast(NDArray[np.float64], optimizer_result.jac)
        conditioning = _conditioning(problem, jacobian)
        return HestonCalibrationResult(
            estimate=estimate,
            objective_value=objective_value,
            residuals=residuals,
            function_evaluations=function_evaluations,
            jacobian_evaluations=jacobian_evaluations,
            termination_status=status,
            termination_message=message,
            conditioning=conditioning,
        )

    def _validate_initial_guess(self, problem: HestonCalibrationProblem) -> None:
        if (
            self.initial_guess.parameters.continuous_dividend_yield
            != problem.continuous_dividend_yield
        ):
            msg = "initial guess must use the calibration problem's fixed dividend yield"
            raise InvalidHestonCalibrationInitialGuess(msg)
        if not problem.bounds.contains(self.initial_guess):
            msg = "initial guess lies outside the admissible Heston calibration domain"
            raise InvalidHestonCalibrationInitialGuess(msg)


def _financial_vector(
    values: NDArray[np.float64],
) -> tuple[float, float, float, float, float]:
    if values.shape != (5,):
        msg = "Heston calibration optimizer vector must contain five coordinates"
        raise ValueError(msg)
    return (
        float(values[0]),
        float(values[1]),
        float(values[2]),
        float(values[3]),
        float(values[4]),
    )


def _conditioning(
    problem: HestonCalibrationProblem,
    weighted_residual_jacobian: NDArray[np.float64],
) -> HestonCalibrationConditioning:
    widths = np.asarray(problem.bounds.widths, dtype=np.float64)
    scaled = weighted_residual_jacobian * widths
    singular_array = svdvals(scaled)
    singular_values = tuple(float(value) for value in singular_array)
    largest = singular_values[0] if singular_values else 0.0
    threshold = max(scaled.shape) * float_info.epsilon * largest
    rank = sum(value > threshold for value in singular_values)
    condition_number: float | None = None
    if rank == 5 and len(singular_values) >= 5 and singular_values[-1] > 0.0:
        candidate = singular_values[0] / singular_values[-1]
        if isfinite(candidate):
            condition_number = candidate
    return HestonCalibrationConditioning(
        singular_values=singular_values,
        jacobian_rank=rank,
        parameter_count=5,
        target_count=len(problem.targets),
        condition_number=condition_number,
    )
