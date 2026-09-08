#!/usr/bin/env python3
"""Calibrate Heston to the pinned M4 SPX option sample from a local raw CSV.

The script intentionally performs no network retrieval. It consumes the same pinned
source artifact and 14 option contracts used by M4's published strike/maturity evidence,
reconstructs raw observations with provenance, normalizes them through the production
M4 midpoint policy, and calibrates the M5 Heston forward model in option-price space.

Raw rows are never written to output. The result contains derived calibration evidence,
contract identifiers, residuals, and source/hash metadata only.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections.abc import Mapping
from datetime import date, datetime
from math import exp
from pathlib import Path

from qf_platform.inference import (
    HestonCalibrationBounds,
    HestonCalibrationCoordinates,
    HestonCalibrationProblem,
    HestonCalibrationWeighting,
    HestonPriceCalibrationTarget,
    ScipyLeastSquaresHestonCalibration,
    calibrate_heston,
)
from qf_platform.market_data import (
    ObservationProvenance,
    OptionExerciseStyle,
    OptionSettlementTime,
    QuoteNormalizationError,
    RawOptionQuote,
    RawUnderlyingObservation,
    normalize_european_option_midpoint,
)
from qf_platform.pricing import (
    FlatMoneyMarketNumeraire,
    HestonFourierEuropeanOption,
    HestonParameters,
    OptionRight,
    PricingMeasureSemantics,
)

_SOURCE_REPOSITORY = "IceCurrent/local_volatility_model"
_SOURCE_COMMIT = "428531599bf3945f5d51691fdd21b1667eb14958"
_SOURCE_PATH = "data/data.csv"
_SOURCE_GIT_BLOB_SHA1 = "8d1db0f2710c4707555c8263f9b7f8f527974836"
_CONTRACT_SEMANTICS_SOURCE = "Cboe SPXW contract specification"
_LICENSE_NOTES = (
    "The pinned public source repository did not contain a license file when M4/M6 "
    "evidence was produced. Raw rows are not redistributed; this recipe records only "
    "a local SHA-256 and derived/model evidence."
)
_PINNED_CONTRACTS: dict[date, frozenset[float]] = {
    date(2023, 2, 3): frozenset({3720.0, 3800.0, 3850.0, 3870.0, 3900.0, 3970.0, 4020.0}),
    date(2023, 4, 28): frozenset({3720.0, 3800.0, 3900.0, 3950.0, 4075.0, 4110.0, 4240.0}),
}


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


def _aware_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        msg = "--retrieved-at must be timezone-aware"
        raise ValueError(msg)
    return parsed


def _artifact_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _clean_header(value: str) -> str:
    return value.strip().strip("[]").strip()


def _clean_row(row: Mapping[str, str | None]) -> dict[str, str | None]:
    return {_clean_header(key): value for key, value in row.items()}


def _required(row: Mapping[str, str | None], key: str) -> str:
    value = row.get(key)
    if value is None or not value.strip():
        msg = f"missing required CSV field {key}"
        raise ValueError(msg)
    return value.strip()


def _market_date(value: str) -> date:
    return date.fromisoformat(value.strip()[:10])


def _raw_observations(
    row: Mapping[str, str | None],
    *,
    right: OptionRight,
    artifact_hash: str,
    retrieved_at: datetime,
) -> tuple[RawOptionQuote, RawUnderlyingObservation]:
    quote_date = _market_date(_required(row, "QUOTE_DATE"))
    expiry = _market_date(_required(row, "EXPIRE_DATE"))
    strike = float(_required(row, "STRIKE"))
    underlying_value = float(_required(row, "UNDERLYING_LAST"))
    prefix = "C" if right is OptionRight.CALL else "P"
    bid = float(_required(row, f"{prefix}_BID"))
    ask = float(_required(row, f"{prefix}_ASK"))
    provenance = ObservationProvenance(
        provider=_SOURCE_REPOSITORY,
        source=(
            f"{_SOURCE_PATH}@{_SOURCE_COMMIT}; contract semantics enriched from "
            f"{_CONTRACT_SEMANTICS_SOURCE}"
        ),
        market_date=quote_date,
        retrieved_at=retrieved_at,
        raw_artifact_sha256=artifact_hash,
        license_notes=_LICENSE_NOTES,
    )
    return (
        RawOptionQuote(
            contract_id=f"SPXW-{expiry.isoformat()}-{right.value}-{strike:g}",
            underlying_id="SPX",
            expiry=expiry,
            strike=strike,
            right=right,
            exercise_style=OptionExerciseStyle.EUROPEAN,
            provenance=provenance,
            bid=bid,
            ask=ask,
            settlement_time=OptionSettlementTime.PM,
        ),
        RawUnderlyingObservation(
            underlying_id="SPX",
            value=underlying_value,
            provenance=provenance,
        ),
    )


def _eligible_otm_side(
    *,
    right: OptionRight,
    strike: float,
    forward: float,
) -> bool:
    if right is OptionRight.PUT:
        return strike < forward
    return strike >= forward


def _market_targets(
    path: Path,
    *,
    artifact_hash: str,
    retrieved_at: datetime,
    rate: float,
    dividend_yield: float,
) -> tuple[tuple[HestonPriceCalibrationTarget, ...], float]:
    valuation_date = date(2023, 1, 4)
    targets: list[HestonPriceCalibrationTarget] = []
    spots: set[float] = set()
    selected_keys: set[tuple[date, float]] = set()
    with path.open(newline="", encoding="utf-8-sig") as handle:
        for raw_row in csv.DictReader(handle):
            row = _clean_row(raw_row)
            try:
                quote_date = _market_date(_required(row, "QUOTE_DATE"))
                expiry = _market_date(_required(row, "EXPIRE_DATE"))
                strike = float(_required(row, "STRIKE"))
            except (KeyError, TypeError, ValueError):
                continue
            if quote_date != valuation_date:
                continue
            if expiry not in _PINNED_CONTRACTS or strike not in _PINNED_CONTRACTS[expiry]:
                continue
            if (expiry, strike) in selected_keys:
                continue

            year_fraction = (expiry - valuation_date).days / 365.0
            for right in (OptionRight.PUT, OptionRight.CALL):
                try:
                    quote, underlying = _raw_observations(
                        row,
                        right=right,
                        artifact_hash=artifact_hash,
                        retrieved_at=retrieved_at,
                    )
                    observation = normalize_european_option_midpoint(quote, underlying)
                except (KeyError, TypeError, ValueError, QuoteNormalizationError):
                    continue
                forward = observation.spot * exp(
                    (rate - dividend_yield) * year_fraction
                )
                if not _eligible_otm_side(
                    right=right,
                    strike=strike,
                    forward=forward,
                ):
                    continue
                targets.append(
                    HestonPriceCalibrationTarget.from_normalized_observation(observation)
                )
                spots.add(observation.spot)
                selected_keys.add((expiry, strike))
                break

    expected_count = sum(len(strikes) for strikes in _PINNED_CONTRACTS.values())
    if len(targets) != expected_count:
        msg = f"expected {expected_count} pinned normalized targets, found {len(targets)}"
        raise ValueError(msg)
    if len(spots) != 1:
        msg = "pinned SPX calibration requires exactly one observed underlying level"
        raise ValueError(msg)
    targets.sort(key=lambda item: (item.contract.expiry, item.contract.strike))
    return tuple(targets), next(iter(spots))


def _coordinates(values: tuple[float, float, float, float, float], *, q: float) -> HestonCalibrationCoordinates:
    return HestonCalibrationCoordinates.from_vector(
        values,
        continuous_dividend_yield=q,
    )


def _result_payload(result: object) -> dict[str, object]:
    estimate = result.estimate
    parameters = estimate.parameters
    return {
        "initial_variance": estimate.initial_variance,
        "mean_reversion_speed": parameters.mean_reversion_speed,
        "long_run_variance": parameters.long_run_variance,
        "volatility_of_variance": parameters.volatility_of_variance,
        "correlation": parameters.correlation,
        "feller_discriminant": parameters.feller_discriminant,
        "feller_condition_satisfied": parameters.feller_condition_satisfied,
        "objective_value": result.objective_value,
        "max_absolute_standardized_residual": result.max_absolute_standardized_residual,
        "function_evaluations": result.function_evaluations,
        "jacobian_evaluations": result.jacobian_evaluations,
        "termination_status": result.termination_status,
        "termination_message": result.termination_message,
        "jacobian_rank": result.conditioning.jacobian_rank,
        "singular_values": list(result.conditioning.singular_values),
        "condition_number": result.conditioning.condition_number,
    }


def derive_evidence(args: argparse.Namespace) -> dict[str, object]:
    if not args.spxw_european_pm:
        msg = "SPXW European/PM semantics must be explicitly confirmed"
        raise ValueError(msg)
    retrieved_at = _aware_datetime(args.retrieved_at)
    artifact_hash = _artifact_sha256(args.csv_path)
    rate = 0.045
    dividend_yield = 0.017
    targets, spot = _market_targets(
        args.csv_path,
        artifact_hash=artifact_hash,
        retrieved_at=retrieved_at,
        rate=rate,
        dividend_yield=dividend_yield,
    )
    valuation_date = date(2023, 1, 4)
    numeraire = FlatMoneyMarketNumeraire(
        reference_date=valuation_date,
        continuously_compounded_rate=rate,
    )
    measure = PricingMeasureSemantics(name="Q^N", numeraire=numeraire)
    problem = HestonCalibrationProblem(
        valuation_date=valuation_date,
        spot=spot,
        targets=targets,
        numeraire=numeraire,
        pricing_measure=measure,
        continuous_dividend_yield=dividend_yield,
        bounds=HestonCalibrationBounds(),
        weighting=HestonCalibrationWeighting.BID_ASK_HALF_SPREAD,
        forward_method=HestonFourierEuropeanOption(
            integration_upper_bound=100.0,
            intervals=256,
        ),
    )
    starts = (
        _coordinates((0.04, 2.0, 0.04, 0.5, -0.7), q=dividend_yield),
        _coordinates((0.06, 1.0, 0.06, 0.8, -0.4), q=dividend_yield),
        _coordinates((0.02, 5.0, 0.02, 0.3, -0.85), q=dividend_yield),
    )
    results = tuple(
        calibrate_heston(
            problem,
            ScipyLeastSquaresHestonCalibration(initial_guess=start),
        )
        for start in starts
    )
    best = min(results, key=lambda item: item.objective_value)
    residuals = [
        {
            "contract_id": item.target.label,
            "expiry": item.target.contract.expiry.isoformat(),
            "strike": item.target.contract.strike,
            "right": item.target.contract.right.value,
            "model_minus_observed_price": item.residual,
            "standardized_by_half_spread": item.standardized_residual,
        }
        for item in best.residuals
    ]
    return {
        "evidence_kind": "derived Heston price-space calibration evidence",
        "source": {
            "repository": _SOURCE_REPOSITORY,
            "commit": _SOURCE_COMMIT,
            "path": _SOURCE_PATH,
            "git_blob_sha1": _SOURCE_GIT_BLOB_SHA1,
            "local_artifact_sha256": artifact_hash,
            "license_note": _LICENSE_NOTES,
        },
        "market_snapshot": {
            "quote_date": valuation_date.isoformat(),
            "underlying": "SPX",
            "observed_spot": spot,
            "selected_expiries": [item.isoformat() for item in _PINNED_CONTRACTS],
            "target_count": len(targets),
            "selection": "same 14 pinned M4 OTM-side contracts",
        },
        "calibration_problem": {
            "target_space": "option price",
            "weighting": HestonCalibrationWeighting.BID_ASK_HALF_SPREAD.value,
            "continuously_compounded_rate": rate,
            "continuous_dividend_yield": dividend_yield,
            "time_basis": "ACT/365F",
            "unknown_coordinates": ["v0", "kappa", "theta", "xi", "rho"],
            "parameter_transform": None,
            "feller_constraint_enforced": False,
            "forward_method": "HestonFourierEuropeanOption",
            "fourier_upper_bound": 100.0,
            "fourier_intervals": 256,
        },
        "best_result": _result_payload(best),
        "multiple_start_results": [_result_payload(result) for result in results],
        "residuals": residuals,
        "interpretation": {
            "optimizer_convergence_is_not_model_validation": True,
            "objective_is_sum_squared_half_spread_standardized_price_residuals": True,
            "conditioning_uses_domain_scaled_weighted_residual_jacobian": True,
        },
    }


def main() -> None:
    args = _parse_args()
    evidence = derive_evidence(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
