"""Synthetic Heston recovery and a thin-sample identifiability counterexample."""

from qf_platform.application import (
    HestonCalibrationWorkbenchAnalysis,
    HestonCalibrationWorkbenchRequest,
    run_heston_calibration,
)
from qf_platform.inference import HestonCalibrationCoordinates
from qf_platform.pricing import HestonParameters


def run_example() -> tuple[
    HestonCalibrationWorkbenchAnalysis, HestonCalibrationWorkbenchAnalysis
]:
    initial_guess = HestonCalibrationCoordinates(
        initial_variance=0.06,
        parameters=HestonParameters(
            mean_reversion_speed=1.2,
            long_run_variance=0.06,
            volatility_of_variance=0.8,
            correlation=-0.4,
            continuous_dividend_yield=0.01,
        ),
    )
    # These two curated modes own fixed synthetic targets/bounds/alternative starts.
    # For custom targets use inference.HestonCalibrationProblem + calibrate_heston.
    recovery = run_heston_calibration(
        HestonCalibrationWorkbenchRequest("recovery", initial_guess, 250, 128)
    )
    thin = run_heston_calibration(
        HestonCalibrationWorkbenchRequest("thin", initial_guess, 250, 128)
    )
    return recovery, thin


if __name__ == "__main__":
    for analysis in run_example():
        print("Synthetic mode:", analysis.mode, "truth:", analysis.truth.as_vector())
        for run in analysis.runs:
            print(run.label, run.result.estimate.as_vector())
            print("Objective:", run.result.objective_value)
            print("Conditioning:", run.result.conditioning)
    print("Small residuals and optimizer convergence do not prove identification.")
