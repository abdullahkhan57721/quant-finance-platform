#!/usr/bin/env python3
"""Compare same-run M8 baseline and optimized performance evidence."""

from __future__ import annotations

import argparse
import json
from math import isfinite, sqrt
from pathlib import Path
from typing import Any, cast

_HEAVY_WORKLOADS = (
    "heston_mc_reference",
    "heston_training_calibration",
    "heston_full_sample_stability_calibration",
    "m7_end_to_end_cross_sectional_validation",
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", required=True, type=Path)
    parser.add_argument("--optimized", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def _load(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def _median(payload: dict[str, Any], workload: str) -> float:
    value = payload["workloads"][workload]["median_seconds_per_invocation"]
    return float(value)


def _output(payload: dict[str, Any], workload: str) -> dict[str, Any]:
    return cast(dict[str, Any], payload["workloads"][workload]["output"])


def _close(left: float, right: float, *, atol: float, rtol: float) -> bool:
    return abs(left - right) <= atol + rtol * max(abs(left), abs(right))


def _deterministic_checks(
    baseline: dict[str, Any],
    optimized: dict[str, Any],
) -> dict[str, object]:
    bs_before = float(_output(baseline, "bs_closed_form_single")["present_value"])
    bs_after = float(_output(optimized, "bs_closed_form_single")["present_value"])
    fourier_before = float(_output(baseline, "heston_fourier_single")["present_value"])
    fourier_after = float(_output(optimized, "heston_fourier_single")["present_value"])

    train_before = _output(baseline, "heston_training_calibration")
    train_after = _output(optimized, "heston_training_calibration")
    full_before = _output(baseline, "heston_full_sample_stability_calibration")
    full_after = _output(optimized, "heston_full_sample_stability_calibration")
    m7_before = _output(baseline, "m7_end_to_end_cross_sectional_validation")
    m7_after = _output(optimized, "m7_end_to_end_cross_sectional_validation")

    train_objectives_before = [float(item["objective_value"]) for item in train_before["starts"]]
    train_objectives_after = [float(item["objective_value"]) for item in train_after["starts"]]
    full_objectives_before = [float(item["objective_value"]) for item in full_before["starts"]]
    full_objectives_after = [float(item["objective_value"]) for item in full_after["starts"]]

    checks = {
        "black_scholes_value_close": _close(
            bs_before,
            bs_after,
            atol=1.0e-12,
            rtol=1.0e-12,
        ),
        "scalar_heston_fourier_value_close": _close(
            fourier_before,
            fourier_after,
            atol=1.0e-12,
            rtol=1.0e-12,
        ),
        "training_objectives_close": all(
            _close(before, after, atol=2.0e-7, rtol=5.0e-8)
            for before, after in zip(
                train_objectives_before,
                train_objectives_after,
                strict=True,
            )
        ),
        "full_sample_objectives_close": all(
            _close(before, after, atol=2.0e-7, rtol=5.0e-8)
            for before, after in zip(
                full_objectives_before,
                full_objectives_after,
                strict=True,
            )
        ),
        "m7_black_scholes_rmse_close": _close(
            float(m7_before["black_scholes_evaluation_rmse"]),
            float(m7_after["black_scholes_evaluation_rmse"]),
            atol=1.0e-8,
            rtol=1.0e-8,
        ),
        "m7_heston_rmse_close": _close(
            float(m7_before["heston_evaluation_rmse"]),
            float(m7_after["heston_evaluation_rmse"]),
            atol=1.0e-5,
            rtol=2.0e-5,
        ),
    }
    return {
        "checks": checks,
        "all_passed": all(checks.values()),
        "note": (
            "Calibration uses the same financial problem and scalar final residual "
            "reconstruction; tiny optimizer-coordinate differences are expected from "
            "batched floating-point summation order."
        ),
    }


def _mc_statistical_check(
    baseline: dict[str, Any],
    optimized: dict[str, Any],
) -> dict[str, object]:
    before = _output(baseline, "heston_mc_reference")
    after = _output(optimized, "heston_mc_reference")
    before_value = float(before["present_value"])
    after_value = float(after["present_value"])
    before_se = float(before["standard_error"])
    after_se = float(after["standard_error"])
    combined_se = sqrt(before_se * before_se + after_se * after_se)
    z_distance = abs(before_value - after_value) / combined_se
    return {
        "baseline_present_value": before_value,
        "optimized_present_value": after_value,
        "baseline_standard_error": before_se,
        "optimized_standard_error": after_se,
        "combined_standard_error": combined_se,
        "absolute_difference_in_combined_se": z_distance,
        "within_four_combined_standard_errors": z_distance <= 4.0,
        "same_paths": before["paths"] == after["paths"],
        "same_time_steps": before["time_steps"] == after["time_steps"],
        "same_seed_configuration": before["seed"] == after["seed"],
        "note": (
            "The M8 vectorized method deliberately changed the local RNG implementation "
            "from scalar random.Random to NumPy PCG64. Equal integer seeds do not imply "
            "identical streams; this is a statistical parity check, not strict stream parity."
        ),
    }


def compare(
    baseline: dict[str, Any],
    optimized: dict[str, Any],
) -> dict[str, object]:
    workload_names = tuple(cast(dict[str, Any], baseline["workloads"]).keys())
    comparisons: dict[str, object] = {}
    for workload in workload_names:
        before = _median(baseline, workload)
        after = _median(optimized, workload)
        speedup = before / after
        if not isfinite(speedup) or speedup <= 0.0:
            msg = f"invalid speedup for {workload}"
            raise ValueError(msg)
        comparisons[workload] = {
            "baseline_median_seconds": before,
            "optimized_median_seconds": after,
            "speedup_x": speedup,
            "baseline_min_seconds": float(
                baseline["workloads"][workload]["minimum_seconds_per_invocation"]
            ),
            "baseline_max_seconds": float(
                baseline["workloads"][workload]["maximum_seconds_per_invocation"]
            ),
            "optimized_min_seconds": float(
                optimized["workloads"][workload]["minimum_seconds_per_invocation"]
            ),
            "optimized_max_seconds": float(
                optimized["workloads"][workload]["maximum_seconds_per_invocation"]
            ),
        }

    heavy_speedups = [
        float(cast(dict[str, Any], comparisons[name])["speedup_x"])
        for name in _HEAVY_WORKLOADS
    ]
    return {
        "evidence_kind": "M8 same-run baseline-versus-optimized comparison",
        "baseline_revision": baseline["environment"]["git_sha"],
        "optimized_revision": optimized["environment"]["git_sha"],
        "same_runner": {
            "baseline_runner_name": baseline["environment"].get("runner_name"),
            "optimized_runner_name": optimized["environment"].get("runner_name"),
            "runner_name_matches": baseline["environment"].get("runner_name")
            == optimized["environment"].get("runner_name"),
            "platform_matches": baseline["environment"].get("platform")
            == optimized["environment"].get("platform"),
            "python_matches": baseline["environment"].get("python")
            == optimized["environment"].get("python"),
            "numpy_matches": baseline["environment"].get("numpy")
            == optimized["environment"].get("numpy"),
            "scipy_matches": baseline["environment"].get("scipy")
            == optimized["environment"].get("scipy"),
        },
        "methodology": optimized["methodology"],
        "workloads": comparisons,
        "deterministic_financial_parity": _deterministic_checks(
            baseline,
            optimized,
        ),
        "monte_carlo_statistical_parity": _mc_statistical_check(
            baseline,
            optimized,
        ),
        "all_heavy_workloads_faster": all(value > 1.0 for value in heavy_speedups),
        "minimum_heavy_workload_speedup_x": min(heavy_speedups),
        "interpretation": (
            "Speedups are descriptive same-run evidence, not CI thresholds. The native "
            "decision must weigh remaining absolute latency against audit/build/packaging "
            "cost, not merely the existence of a remaining hotspot."
        ),
    }


def main() -> None:
    args = _parse_args()
    payload = compare(_load(args.baseline), _load(args.optimized))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
