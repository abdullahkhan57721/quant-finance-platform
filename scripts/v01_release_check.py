#!/usr/bin/env python3
"""Verify the v0.1 release metadata and committed M7/M8 evidence."""

from __future__ import annotations

import json
import math
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

_DISTRIBUTION = "quant-finance-platform"
_EXPECTED_VERSION = "0.1.0"
_REPO_ROOT = Path(__file__).resolve().parents[1]
_M7_PATH = _REPO_ROOT / "docs/evidence/m7_spx_bs_vs_heston_validation_reference.json"
_M8_PATH = _REPO_ROOT / "docs/evidence/m8_performance_reference.json"


def _load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        msg = f"expected object at {path}"
        raise TypeError(msg)
    return payload


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _require_close(actual: float, expected: float, label: str) -> None:
    if not math.isclose(actual, expected, rel_tol=1e-10, abs_tol=1e-12):
        msg = f"{label}: expected {expected}, observed {actual}"
        raise RuntimeError(msg)


def _installed_version() -> str:
    try:
        return version(_DISTRIBUTION)
    except PackageNotFoundError as exc:
        msg = (
            "quant-finance-platform is not installed; install the repository before "
            "running the v0.1 release check"
        )
        raise RuntimeError(msg) from exc


def _verify_m7(payload: dict[str, Any]) -> tuple[float, float]:
    partition = payload["predeclared_partition"]
    _require(partition["training_count"] == 10, "M7 training count drifted")
    _require(partition["evaluation_count"] == 4, "M7 evaluation count drifted")
    _require(
        partition["temporal_out_of_sample"] is False,
        "M7 must not be presented as temporal out-of-sample evidence",
    )

    conclusion = payload["conclusion"]
    _require(
        conclusion["temporal_out_of_sample_tested"] is False,
        "M7 temporal non-claim drifted",
    )
    _require(
        conclusion["heston_hedge_comparison_supported"] is False,
        "M7 must not claim Heston hedge comparison support",
    )
    _require(
        conclusion["heston_lower_evaluation_price_rmse"] is True,
        "M7 headline held-out price-RMSE ordering drifted",
    )

    metrics = payload["metrics"]
    bs = metrics["black_scholes_evaluation"]
    heston = metrics["heston_evaluation"]
    bs_rmse = float(bs["root_mean_square_error"])
    heston_rmse = float(heston["root_mean_square_error"])

    _require_close(bs_rmse, 8.411568152765, "M7 Black-Scholes held-out RMSE")
    _require_close(heston_rmse, 0.671234847137, "M7 Heston held-out RMSE")
    _require_close(
        float(bs["relative_mean_absolute_error"]),
        0.082689508631,
        "M7 Black-Scholes held-out relative MAE",
    )
    _require_close(
        float(heston["relative_mean_absolute_error"]),
        0.006551442606,
        "M7 Heston held-out relative MAE",
    )
    _require(heston_rmse < bs_rmse, "M7 held-out RMSE ordering drifted")
    return bs_rmse, heston_rmse


def _verify_m8(payload: dict[str, Any]) -> tuple[float, float]:
    workloads = payload["workloads"]
    heavy_ids = (
        "heston_mc_reference",
        "heston_training_calibration",
        "heston_full_sample_stability_calibration",
        "m7_end_to_end_cross_sectional_validation",
    )
    speedups = [float(workloads[item]["speedup_x"]) for item in heavy_ids]
    minimum = min(speedups)
    maximum = max(speedups)
    _require_close(minimum, 4.610210, "M8 minimum heavy-workload speedup")
    _require_close(maximum, 27.381282, "M8 maximum heavy-workload speedup")

    parity = payload["parity"]
    _require(
        parity["deterministic_checks"]["all_passed"] is True,
        "M8 deterministic parity evidence drifted",
    )
    mc = parity["heston_monte_carlo"]
    _require(
        mc["within_four_combined_standard_errors"] is True,
        "M8 Monte Carlo statistical parity evidence drifted",
    )
    _require(
        mc["identical_rng_stream_claimed"] is False,
        "M8 must not claim identical old/new RNG streams",
    )

    native = payload["native_decision"]
    _require(native["cpp_added"] is False, "v0.1 must not claim a C++ kernel")
    _require(
        "not justified" in str(native["decision"]),
        "M8 measured no-C++ decision drifted",
    )
    return minimum, maximum


def main() -> int:
    installed = _installed_version()
    _require(
        installed == _EXPECTED_VERSION,
        f"installed version must be {_EXPECTED_VERSION}, observed {installed}",
    )

    bs_rmse, heston_rmse = _verify_m7(_load_json(_M7_PATH))
    minimum_speedup, maximum_speedup = _verify_m8(_load_json(_M8_PATH))

    print(f"v{installed} release verification passed")
    print(
        "M7: 10 training / 4 held-out; "
        f"price RMSE {bs_rmse:.3f} -> {heston_rmse:.3f}"
    )
    print(
        "M8: heavy-workload speedups "
        f"{minimum_speedup:.2f}x-{maximum_speedup:.2f}x; C++ added: no"
    )
    print(
        "Raw-market replay remains separate and requires the pinned local source "
        "artifact; raw rows are not redistributed."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
