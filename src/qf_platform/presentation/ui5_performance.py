"""Renderer-neutral UI5 presentation of committed M8 performance evidence."""

from __future__ import annotations

from dataclasses import dataclass

from qf_platform.application.ui5_performance import UI5PerformanceReference
from qf_platform.presentation.black_scholes import PresentationRow
from qf_platform.presentation.plotting import PlotData, PlotPoint, PlotSeries


@dataclass(frozen=True, slots=True)
class UI5PerformancePresentation:
    """Concrete product-facing M8 evidence without a generic benchmark framework."""

    workload_rows: tuple[PresentationRow, ...]
    parity_rows: tuple[PresentationRow, ...]
    native_decision_rows: tuple[PresentationRow, ...]
    provenance_rows: tuple[PresentationRow, ...]
    runtime_plot: PlotData
    report_text: str


def build_ui5_performance_presentation(
    reference: UI5PerformanceReference,
) -> UI5PerformancePresentation:
    """Translate the revision-pinned M8 reference into renderer-neutral values."""

    workload_rows = tuple(
        PresentationRow(
            label=workload.label,
            value=(
                f"{workload.baseline_median_seconds:.6f} s → "
                f"{workload.optimized_median_seconds:.6f} s"
            ),
            detail=workload.detail,
            status=(
                f"{workload.speedup_x:.2f}× measured speedup"
                if workload.heavy_workload
                else "Scalar reference · no speedup claim"
            ),
        )
        for workload in reference.workloads
    )
    parity_rows = (
        PresentationRow(
            label="Deterministic parity",
            value="PASS"
            if reference.parity.deterministic_checks_all_passed
            else "FAIL",
            detail=(
                "Black-Scholes value, scalar Heston Fourier value, calibration objectives, "
                "and M7 held-out RMSE checks."
            ),
            status="Authoritative M8 comparison",
        ),
        PresentationRow(
            label="Heston Monte Carlo parity",
            value=(
                f"{reference.parity.monte_carlo_difference_in_combined_standard_errors:.3f} "
                "combined standard errors"
            ),
            detail=(
                "Old and optimized methods use different RNG algorithms, so parity is "
                "statistical rather than streamwise."
            ),
            status=(
                "Within 4-SE comparison bound"
                if reference.parity.monte_carlo_within_four_combined_standard_errors
                else "Outside 4-SE comparison bound"
            ),
        ),
        PresentationRow(
            label="Identical RNG stream claimed",
            value="Yes" if reference.parity.identical_rng_stream_claimed else "No",
            detail="Equal integer seed does not imply equal pre-M8/post-M8 random streams.",
            status=reference.parity.monte_carlo_parity_kind.title(),
        ),
    )
    native_decision_rows = (
        PresentationRow(
            label="C++ kernel added",
            value="Yes" if reference.cpp_added else "No",
            detail=reference.native_reason,
            status="Measured negative native decision"
            if not reference.cpp_added
            else "Native path",
        ),
        PresentationRow(
            label="Minimum heavy-workload speedup",
            value=f"{reference.minimum_heavy_workload_speedup_x:.2f}×",
            detail=(
                "Python/NumPy optimization removed enough measured cost that a compiler, "
                "binding and extra parity surface is not justified for v0.1."
            ),
            status="Python-first optimization",
        ),
        PresentationRow(
            label="Native decision",
            value=reference.native_decision,
            detail=(
                "Future materially larger workloads may reopen the question only after "
                "fresh profiling."
            ),
            status="Not a permanent no-C++ rule",
        ),
    )
    provenance_rows = (
        PresentationRow(
            label="Evidence artifact",
            value=reference.source_artifact_path,
            detail=reference.evidence_kind,
            status="Committed derived evidence",
        ),
        PresentationRow(
            label="Baseline revision",
            value=reference.baseline_revision,
            detail="Frozen merged-M7 reference before M8 optimization.",
            status="Revision pinned",
        ),
        PresentationRow(
            label="Optimized reference revision",
            value=reference.optimized_reference_revision,
            detail=f"Same-run workflow {reference.workflow_run_id}.",
            status="Revision pinned",
        ),
        PresentationRow(
            label="Reference environment",
            value=(
                f"{reference.runner_os}/{reference.runner_architecture} · "
                f"Python {reference.python_version} · NumPy {reference.numpy_version} · "
                f"SciPy {reference.scipy_version}"
            ),
            detail=(
                f"{reference.warmup_samples} warmup + {reference.timing_repetitions} measured "
                "repetitions; medians are descriptive hosted-runner evidence."
            ),
            status=(
                "Not a CI threshold"
                if not reference.timings_are_ci_thresholds
                else "CI threshold"
            ),
        ),
    )
    runtime_plot = PlotData(
        title="M8 representative workload wall time",
        x_label="Representative workload index",
        y_label="Median wall time (seconds)",
        series=(
            PlotSeries(
                key="baseline",
                label="Frozen M7 baseline",
                points=tuple(
                    PlotPoint(x=float(index), y=workload.baseline_median_seconds)
                    for index, workload in enumerate(reference.workloads)
                ),
            ),
            PlotSeries(
                key="optimized",
                label="M8 optimized",
                points=tuple(
                    PlotPoint(x=float(index), y=workload.optimized_median_seconds)
                    for index, workload in enumerate(reference.workloads)
                ),
            ),
        ),
    )
    report_lines = [
        "M8 PERFORMANCE ENGINEERING EVIDENCE",
        "",
        f"Baseline revision: {reference.baseline_revision}",
        f"Optimized reference revision: {reference.optimized_reference_revision}",
        f"Evidence workflow: {reference.workflow_run_id}",
        "",
        "Representative workloads:",
    ]
    report_lines.extend(
        (
            f"- {workload.label}: {workload.baseline_median_seconds:.6f} s -> "
            f"{workload.optimized_median_seconds:.6f} s; {workload.speedup_x:.2f}x"
            + (
                " measured speedup"
                if workload.heavy_workload
                else " (no speedup claim)"
            )
        )
        for workload in reference.workloads
    )
    report_lines.extend(
        [
            "",
            "Parity:",
            f"- deterministic checks passed: {reference.parity.deterministic_checks_all_passed}",
            (
                "- Heston Monte Carlo difference: "
                f"{reference.parity.monte_carlo_difference_in_combined_standard_errors:.3f} "
                "combined standard errors"
            ),
            f"- identical RNG stream claimed: {reference.parity.identical_rng_stream_claimed}",
            "",
            "Native decision:",
            f"- C++ kernel added: {reference.cpp_added}",
            f"- {reference.native_decision}",
            f"- {reference.native_reason}",
        ]
    )
    return UI5PerformancePresentation(
        workload_rows=workload_rows,
        parity_rows=parity_rows,
        native_decision_rows=native_decision_rows,
        provenance_rows=provenance_rows,
        runtime_plot=runtime_plot,
        report_text="\n".join(report_lines),
    )
