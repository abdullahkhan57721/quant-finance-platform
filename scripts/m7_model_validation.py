#!/usr/bin/env python3
"""Compare fitted Black-Scholes and Heston on the pinned M4/M6 SPX sample.

The script performs no network retrieval. It reuses M6's local raw-artifact parser and
M4 normalization path, verifies the exact pinned Git blob, applies M7's predeclared
same-date 10/4 cross-sectional holdout, fits both models on training observations only,
and emits derived validation/model-risk evidence. Raw source rows are never written.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from time import perf_counter

from m6_heston_calibration import (
    _SOURCE_COMMIT,
    _SOURCE_GIT_BLOB_SHA1,
    _SOURCE_PATH,
    _SOURCE_REPOSITORY,
    _artifact_hashes,
    _aware_datetime,
    _market_targets,
)

from qf_platform.inference import HestonCalibrationCoordinates
from qf_platform.market_data import NormalizedOptionObservation
from qf_platform.pricing import (
    FlatMoneyMarketNumeraire,
    HestonFourierEuropeanOption,
    PricingMeasureSemantics,
)
from qf_platform.validation import (
    BlackScholesHestonValidationProblem,
    CrossSectionalBlackScholesHestonValidation,
    HestonStartEvidence,
    predeclared_every_third_evaluation_partition,
    validate_black_scholes_vs_heston,
)

_LICENSE_NOTE = (
    "The pinned public source repository did not contain a license file when M4/M6 "
    "evidence was produced. Raw rows are not redistributed; M7 emits derived model "
    "validation evidence only."
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path)
    parser.add_argument(
        "--retrieved-at",
        required=True,
        help="timezone-aware ISO-8601 timestamp for local artifact retrieval",
    )
    parser.add_argument(
        "--spxw-european-pm",
        required=True,
        action="store_true",
        help="explicitly confirm SPXW European-exercise/PM-settlement semantics",
    )
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def _observations_from_m6_targets(
    targets: tuple[object, ...],
) -> tuple[NormalizedOptionObservation, ...]:
    observations: list[NormalizedOptionObservation] = []
    for target in targets:
        observation = getattr(target, "observation", None)
        if not isinstance(observation, NormalizedOptionObservation):
            msg = "M7 raw replay expected every M6 target to retain M4 observation lineage"
            raise TypeError(msg)
        observations.append(observation)
    return tuple(observations)


def _coordinates(
    values: tuple[float, float, float, float, float],
    *,
    q: float,
) -> HestonCalibrationCoordinates:
    return HestonCalibrationCoordinates.from_vector(
        values,
        continuous_dividend_yield=q,
    )


def _start_payload(item: HestonStartEvidence) -> dict[str, object]:
    payload: dict[str, object] = {
        "initial_guess": list(item.initial_guess.as_vector()),
        "converged": item.converged,
        "failure_message": item.failure_message,
    }
    if item.result is None:
        return payload
    payload.update(
        {
            "estimate": list(item.result.estimate.as_vector()),
            "objective_value": item.result.objective_value,
            "function_evaluations": item.result.function_evaluations,
            "jacobian_evaluations": item.result.jacobian_evaluations,
            "jacobian_rank": item.result.conditioning.jacobian_rank,
            "condition_number": item.result.conditioning.condition_number,
        }
    )
    return payload


def derive_evidence(args: argparse.Namespace) -> dict[str, object]:
    if not args.spxw_european_pm:
        msg = "SPXW European/PM semantics must be explicitly confirmed"
        raise ValueError(msg)
    retrieved_at = _aware_datetime(args.retrieved_at)
    sha256, git_blob_sha1 = _artifact_hashes(args.csv_path)
    if git_blob_sha1 != _SOURCE_GIT_BLOB_SHA1:
        msg = (
            "local CSV does not match the pinned M4/M6 Git blob: "
            f"expected {_SOURCE_GIT_BLOB_SHA1}, observed {git_blob_sha1}"
        )
        raise ValueError(msg)

    rate = 0.045
    q = 0.017
    m6_targets, spot = _market_targets(
        args.csv_path,
        artifact_hash=sha256,
        retrieved_at=retrieved_at,
        rate=rate,
        dividend_yield=q,
    )
    observations = _observations_from_m6_targets(tuple(m6_targets))
    training_ids, evaluation_ids = predeclared_every_third_evaluation_partition(
        observations
    )
    valuation_date = observations[0].valuation_date
    numeraire = FlatMoneyMarketNumeraire(
        reference_date=valuation_date,
        continuously_compounded_rate=rate,
    )
    problem = BlackScholesHestonValidationProblem(
        observations=observations,
        training_contract_ids=training_ids,
        evaluation_contract_ids=evaluation_ids,
        numeraire=numeraire,
        pricing_measure=PricingMeasureSemantics(name="Q^N", numeraire=numeraire),
        continuous_dividend_yield=q,
        heston_forward_method=HestonFourierEuropeanOption(
            integration_upper_bound=100.0,
            intervals=256,
        ),
    )
    starts = (
        _coordinates((0.04, 2.0, 0.04, 0.5, -0.7), q=q),
        _coordinates((0.06, 1.0, 0.06, 0.8, -0.4), q=q),
        _coordinates((0.02, 5.0, 0.02, 0.3, -0.85), q=q),
    )
    method = CrossSectionalBlackScholesHestonValidation(
        black_scholes_initial_volatility=0.21,
        heston_initial_guesses=starts,
    )
    started = perf_counter()
    evidence = validate_black_scholes_vs_heston(problem, method)
    elapsed = perf_counter() - started

    return {
        "evidence_kind": "derived M7 Black-Scholes versus Heston model validation",
        "source": {
            "repository": _SOURCE_REPOSITORY,
            "commit": _SOURCE_COMMIT,
            "path": _SOURCE_PATH,
            "git_blob_sha1": git_blob_sha1,
            "git_blob_verified": True,
            "local_artifact_sha256": sha256,
            "license_note": _LICENSE_NOTE,
        },
        "market_snapshot": {
            "quote_date": valuation_date.isoformat(),
            "underlying": "SPX",
            "observed_spot": spot,
            "observation_count": len(observations),
            "training_count": len(training_ids),
            "evaluation_count": len(evaluation_ids),
            "temporal_out_of_sample": False,
        },
        "predeclared_partition": {
            "rule": "sort by (expiry, strike); evaluation iff zero-based index % 3 == 2",
            "training_contract_ids": list(training_ids),
            "evaluation_contract_ids": list(evaluation_ids),
        },
        "financial_inputs": {
            "continuously_compounded_rate": rate,
            "continuous_dividend_yield": q,
            "time_basis": "ACT/365F",
            "price_target": "bid/ask midpoint",
            "residual_scale": "bid/ask half-spread",
        },
        "black_scholes_training_fit": asdict(evidence.black_scholes_fit),
        "heston_training_starts": [
            _start_payload(item) for item in evidence.heston_training_starts
        ],
        "selected_heston_training_estimate": list(
            evidence.selected_heston_training_result.estimate.as_vector()
        ),
        "heston_full_sample_stability_starts": [
            _start_payload(item) for item in evidence.heston_full_sample_starts
        ],
        "selected_heston_full_sample_estimate": list(
            evidence.selected_heston_full_sample_result.estimate.as_vector()
        ),
        "metrics": {
            "black_scholes_training": asdict(evidence.black_scholes_training_metrics),
            "black_scholes_evaluation": asdict(
                evidence.black_scholes_evaluation_metrics
            ),
            "heston_training": asdict(evidence.heston_training_metrics),
            "heston_evaluation": asdict(evidence.heston_evaluation_metrics),
        },
        "residuals": [
            {
                "contract_id": item.contract_id,
                "model": item.model.value,
                "partition": item.partition.value,
                "expiry": item.expiry.isoformat(),
                "strike": item.strike,
                "right": item.right,
                "log_forward_moneyness": item.log_forward_moneyness,
                "observed_price": item.observed_price,
                "model_price": item.model_price,
                "model_minus_observed_price": item.residual,
                "half_spread": item.half_spread,
                "standardized_residual": item.standardized_residual,
                "relative_absolute_error": item.relative_absolute_error,
            }
            for item in evidence.residuals
        ],
        "heston_parameter_stability": asdict(evidence.heston_stability),
        "structural_computation_evidence": asdict(evidence.computation),
        "environment_dependent_timing": {
            "end_to_end_validation_wall_clock_seconds": elapsed,
            "interpretation": (
                "Exploratory local timing only; not a CI threshold or portable benchmark. "
                "M8 must profile representative workloads before optimization."
            ),
        },
        "m8_representative_workloads": [
            {
                "id": "bs_closed_form_single",
                "operation": "one BlackScholesClosedForm European-option valuation",
            },
            {
                "id": "heston_fourier_single",
                "operation": "one HestonFourierEuropeanOption valuation",
                "integration_upper_bound": 100.0,
                "intervals": 256,
            },
            {
                "id": "heston_mc_reference",
                "operation": "one seeded HestonMonteCarloEuropeanOption valuation",
                "paths": 20000,
                "time_steps": 252,
                "seed": 20260910,
                "note": "profile in M8; not executed by this M7 market replay",
            },
            {
                "id": "heston_training_calibration",
                "operation": "10-target price-space Heston calibration",
                "starts": 3,
            },
            {
                "id": "heston_full_sample_stability_calibration",
                "operation": "14-target price-space Heston stability calibration",
                "starts": 3,
            },
            {
                "id": "m7_end_to_end_cross_sectional_validation",
                "operation": "full 10-train/4-evaluation M7 study",
            },
        ],
        "hedging_evidence_boundary": {
            "m3_integrated": True,
            "heston_generated_world_compared": False,
            "heston_hedge_compared": False,
            "reason": (
                "M3 SimulatedEquityPath is explicitly Black-Scholes/GBM and no "
                "authoritative Heston Delta/hedge execution contract exists."
            ),
        },
        "conclusion": asdict(evidence.conclusion),
    }


def main() -> None:
    args = _parse_args()
    payload = derive_evidence(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
