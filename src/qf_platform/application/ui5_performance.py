"""Frontend-neutral UI5 mirror of the committed M8 performance evidence."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UI5PerformanceWorkload:
    """One revision-pinned M8 representative workload comparison."""

    workload_id: str
    label: str
    baseline_median_seconds: float
    optimized_median_seconds: float
    speedup_x: float
    heavy_workload: bool
    detail: str


@dataclass(frozen=True, slots=True)
class UI5PerformanceParity:
    """Compact parity evidence retained by the M8 reporting reference."""

    deterministic_checks_all_passed: bool
    monte_carlo_parity_kind: str
    monte_carlo_difference_in_combined_standard_errors: float
    monte_carlo_within_four_combined_standard_errors: bool
    identical_rng_stream_claimed: bool


@dataclass(frozen=True, slots=True)
class UI5PerformanceReference:
    """Package-safe mirror of the committed derived M8 performance reference."""

    evidence_kind: str
    source_artifact_path: str
    baseline_revision: str
    optimized_reference_revision: str
    workflow_run_id: int
    runner_os: str
    runner_architecture: str
    python_version: str
    numpy_version: str
    scipy_version: str
    warmup_samples: int
    timing_repetitions: int
    timings_are_ci_thresholds: bool
    workloads: tuple[UI5PerformanceWorkload, ...]
    parity: UI5PerformanceParity
    cpp_added: bool
    native_decision: str
    native_reason: str
    minimum_heavy_workload_speedup_x: float


def canonical_m8_performance_reference() -> UI5PerformanceReference:
    """Return the revision-pinned M8 evidence used by the UI5/M9 product story."""

    return UI5PerformanceReference(
        evidence_kind="M8 same-run baseline-versus-optimized performance reference",
        source_artifact_path="docs/evidence/m8_performance_reference.json",
        baseline_revision="4d80014786810389c324434d7cccab95cf647803",
        optimized_reference_revision="15d3b6c83a16ed660f00e7a6bf085cb57b76c411",
        workflow_run_id=34640269472,
        runner_os="Linux",
        runner_architecture="X64",
        python_version="3.12.14",
        numpy_version="2.5.3",
        scipy_version="1.18.1",
        warmup_samples=1,
        timing_repetitions=3,
        timings_are_ci_thresholds=False,
        workloads=(
            UI5PerformanceWorkload(
                workload_id="bs_closed_form_single",
                label="Black-Scholes scalar",
                baseline_median_seconds=0.000002083384,
                optimized_median_seconds=0.000002271688,
                speedup_x=0.917108,
                heavy_workload=False,
                detail=(
                    "Readable scalar reference; microbenchmark difference is runner/process "
                    "noise, not a performance claim."
                ),
            ),
            UI5PerformanceWorkload(
                workload_id="heston_fourier_single",
                label="Heston Fourier scalar",
                baseline_median_seconds=0.0007491704,
                optimized_median_seconds=0.00081811415,
                speedup_x=0.915733,
                heavy_workload=False,
                detail=(
                    "Readable scalar Fourier reference intentionally retained rather than "
                    "optimized."
                ),
            ),
            UI5PerformanceWorkload(
                workload_id="heston_mc_reference",
                label="Heston MC · 20k × 252",
                baseline_median_seconds=3.367340221,
                optimized_median_seconds=0.122979639,
                speedup_x=27.381282,
                heavy_workload=True,
                detail=(
                    "20,000 paths, 252 timesteps, 5,040,000 path-step transitions and "
                    "10,080,000 Gaussian draws."
                ),
            ),
            UI5PerformanceWorkload(
                workload_id="heston_training_calibration",
                label="Heston calibration · 10 targets",
                baseline_median_seconds=2.291878464,
                optimized_median_seconds=0.497131053,
                speedup_x=4.610210,
                heavy_workload=True,
                detail="10 training targets and 3 predeclared optimizer starts.",
            ),
            UI5PerformanceWorkload(
                workload_id="heston_full_sample_stability_calibration",
                label="Heston stability · 14 targets",
                baseline_median_seconds=3.275180944,
                optimized_median_seconds=0.545351821,
                speedup_x=6.005629,
                heavy_workload=True,
                detail="14 full-sample targets and 3 predeclared optimizer starts.",
            ),
            UI5PerformanceWorkload(
                workload_id="m7_end_to_end_cross_sectional_validation",
                label="Complete M7 validation",
                baseline_median_seconds=5.413630502,
                optimized_median_seconds=1.081868411,
                speedup_x=5.003964,
                heavy_workload=True,
                detail="10 training / 4 held-out M7 cross-sectional validation study.",
            ),
        ),
        parity=UI5PerformanceParity(
            deterministic_checks_all_passed=True,
            monte_carlo_parity_kind="statistical",
            monte_carlo_difference_in_combined_standard_errors=0.852814878,
            monte_carlo_within_four_combined_standard_errors=True,
            identical_rng_stream_claimed=False,
        ),
        cpp_added=False,
        native_decision=(
            "not justified for the v0.1 representative workloads after Python/algorithmic "
            "optimization"
        ),
        native_reason=(
            "all heavy workloads improved by at least about 4.61x while representative "
            "post-optimization absolute runtimes became small enough that a new "
            "compiler/binding/cross-platform packaging and parity surface would not justify "
            "its auditability and maintenance cost"
        ),
        minimum_heavy_workload_speedup_x=4.610210,
    )
