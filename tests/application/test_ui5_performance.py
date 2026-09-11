from __future__ import annotations

import json
from pathlib import Path

import pytest

from qf_platform.application.ui5_performance import canonical_m8_performance_reference


def test_ui5_performance_reference_matches_committed_m8_evidence() -> None:
    reference = canonical_m8_performance_reference()
    artifact_path = Path(reference.source_artifact_path)
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert reference.evidence_kind == artifact["evidence_kind"]
    assert reference.baseline_revision == artifact["baseline_revision"]
    assert (
        reference.optimized_reference_revision
        == artifact["optimized_reference_revision"]
    )
    assert reference.workflow_run_id == artifact["workflow_run_id"]
    assert reference.runner_os == artifact["environment"]["runner_os"]
    assert reference.runner_architecture == artifact["environment"]["runner_arch"]
    assert reference.python_version == artifact["environment"]["python"]
    assert reference.numpy_version == artifact["environment"]["numpy"]
    assert reference.scipy_version == artifact["environment"]["scipy"]
    assert reference.warmup_samples == artifact["methodology"]["warmup_samples"]
    assert reference.timing_repetitions == artifact["methodology"]["timing_repetitions"]
    assert (
        reference.timings_are_ci_thresholds
        is artifact["methodology"]["timings_are_ci_thresholds"]
    )

    assert len(reference.workloads) == len(artifact["workloads"]) == 6
    for workload in reference.workloads:
        recorded = artifact["workloads"][workload.workload_id]
        assert workload.baseline_median_seconds == pytest.approx(
            recorded["baseline_median_seconds"]
        )
        assert workload.optimized_median_seconds == pytest.approx(
            recorded["optimized_median_seconds"]
        )
        assert workload.speedup_x == pytest.approx(recorded["speedup_x"])

    mc_parity = artifact["parity"]["heston_monte_carlo"]
    assert (
        reference.parity.deterministic_checks_all_passed
        is artifact["parity"]["deterministic_checks"]["all_passed"]
    )
    assert reference.parity.monte_carlo_parity_kind == mc_parity["parity_kind"]
    assert reference.parity.monte_carlo_difference_in_combined_standard_errors == (
        pytest.approx(mc_parity["absolute_difference_in_combined_standard_errors"])
    )
    assert (
        reference.parity.monte_carlo_within_four_combined_standard_errors
        is mc_parity["within_four_combined_standard_errors"]
    )
    assert (
        reference.parity.identical_rng_stream_claimed
        is mc_parity["identical_rng_stream_claimed"]
    )

    native = artifact["native_decision"]
    assert reference.cpp_added is native["cpp_added"]
    assert reference.native_decision == native["decision"]
    assert reference.native_reason == native["reason"]
    assert reference.minimum_heavy_workload_speedup_x == pytest.approx(
        native["minimum_heavy_workload_speedup_x"]
    )


def test_ui5_performance_reference_keeps_scalar_and_heavy_claims_distinct() -> None:
    reference = canonical_m8_performance_reference()
    scalar = tuple(
        workload for workload in reference.workloads if not workload.heavy_workload
    )
    heavy = tuple(
        workload for workload in reference.workloads if workload.heavy_workload
    )

    assert {workload.workload_id for workload in scalar} == {
        "bs_closed_form_single",
        "heston_fourier_single",
    }
    assert len(heavy) == 4
    assert min(workload.speedup_x for workload in heavy) == pytest.approx(
        reference.minimum_heavy_workload_speedup_x
    )
    assert not reference.cpp_added
    assert not reference.timings_are_ci_thresholds
