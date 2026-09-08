#!/usr/bin/env python3
"""Derive M4 SPX implied-volatility evidence from a pinned local CSV artifact.

This script intentionally performs no network retrieval. The reproducible M4 research
input is the public SPX snapshot at ``IceCurrent/local_volatility_model`` commit
``428531599bf3945f5d51691fdd21b1667eb14958``, path ``data/data.csv``. The CSV
contains quote/expiry/strike/underlying and call/put bid/ask fields, but not exercise
style or settlement time. The caller must therefore explicitly opt into the separately
verified SPXW European/PM contract semantics before inference.

The raw artifact is hashed locally. Output contains derived/model evidence and
provenance metadata only; raw rows are never copied into the result.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from collections.abc import Mapping
from datetime import date, datetime
from math import exp
from pathlib import Path

from qf_platform.inference import (
    BisectionImpliedVolatility,
    BlackScholesImpliedVolatilityProblem,
    ImpliedVolatilityConvergenceError,
    ImpliedVolatilityNotBracketed,
    ImpliedVolatilityResult,
    InconsistentObservedPrice,
    InvalidImpliedVolatilityProblem,
    infer_implied_volatility,
    log_forward_moneyness,
)
from qf_platform.market_data import (
    IncomparableOptionSlice,
    NormalizedOptionObservation,
    ObservationProvenance,
    OptionExerciseStyle,
    OptionSettlementTime,
    OptionSliceDiagnostics,
    QuoteNormalizationError,
    RawOptionQuote,
    RawUnderlyingObservation,
    diagnose_option_strike_slice,
    normalize_european_option_midpoint,
)
from qf_platform.pricing import (
    FlatMoneyMarketNumeraire,
    OptionRight,
    PricingMeasureSemantics,
)

_SOURCE_REPOSITORY = "IceCurrent/local_volatility_model"
_SOURCE_COMMIT = "428531599bf3945f5d51691fdd21b1667eb14958"
_SOURCE_PATH = "data/data.csv"
_SOURCE_GIT_BLOB_SHA1 = "8d1db0f2710c4707555c8263f9b7f8f527974836"
_CONTRACT_SEMANTICS_SOURCE = "Cboe SPXW contract specification"
_LICENSE_NOTES = (
    "The pinned public source repository did not contain a license file when M4 was "
    "produced. Raw rows are not redistributed by this repository; this recipe records "
    "only a local SHA-256 and derived/model evidence."
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--quote-date", required=True, type=date.fromisoformat)
    parser.add_argument(
        "--expiry",
        required=True,
        action="append",
        type=date.fromisoformat,
        help="repeat for each expiry to include",
    )
    parser.add_argument("--rate", required=True, type=float)
    parser.add_argument("--dividend-yield", required=True, type=float)
    parser.add_argument(
        "--retrieved-at",
        required=True,
        help="timezone-aware ISO-8601 timestamp for local artifact retrieval",
    )
    parser.add_argument(
        "--spxw-european-pm",
        required=True,
        action="store_true",
        help=(
            "explicitly confirm separate SPXW European-exercise/PM-settlement "
            "contract semantics for the selected non-third-Friday expiries"
        ),
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
    underlying = RawUnderlyingObservation(
        underlying_id="SPX",
        value=underlying_value,
        provenance=provenance,
    )
    quote = RawOptionQuote(
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
    )
    return quote, underlying


def _eligible_otm_side(quote: RawOptionQuote, *, forward: float) -> bool:
    if quote.right is OptionRight.PUT:
        return quote.strike < forward
    return quote.strike >= forward


def _point(
    result: ImpliedVolatilityResult,
    problem: BlackScholesImpliedVolatilityProblem,
) -> dict[str, object]:
    return {
        "expiry": problem.observation.raw_quote.expiry.isoformat(),
        "strike": problem.observation.raw_quote.strike,
        "right": problem.observation.raw_quote.right.value,
        "moneyness": result.moneyness,
        "log_forward_moneyness": log_forward_moneyness(problem),
        "annualized_implied_volatility": result.annualized_volatility,
        "vega_per_1_00_volatility": result.vega,
        "volatility_change_per_price_unit": result.volatility_change_per_price_unit,
        "local_volatility_shift_for_half_spread": (
            result.local_volatility_shift_for_half_spread
        ),
        "normalization_version": problem.observation.normalization_version,
    }


def _diagnostics_payload(
    diagnostics: OptionSliceDiagnostics,
) -> dict[str, object]:
    return {
        "right": diagnostics.right.value,
        "strikes_checked": len(diagnostics.strikes),
        "passes_checked_conditions": diagnostics.passes,
        "monotonicity_violations": [list(pair) for pair in diagnostics.monotonicity_violations],
        "convexity_violations": [list(triple) for triple in diagnostics.convexity_violations],
    }


def _slice_diagnostics(
    observations: list[NormalizedOptionObservation],
) -> dict[str, object] | None:
    try:
        return _diagnostics_payload(diagnose_option_strike_slice(observations))
    except IncomparableOptionSlice:
        return None


def derive_evidence(args: argparse.Namespace) -> dict[str, object]:
    path = args.csv_path
    retrieved_at = _aware_datetime(args.retrieved_at)
    artifact_hash = _artifact_sha256(path)
    selected_expiries = frozenset(args.expiry)
    exclusions: Counter[str] = Counter()
    inferred_by_expiry: dict[date, list[dict[str, object]]] = {
        expiry: [] for expiry in selected_expiries
    }
    calls_by_expiry: dict[date, list[NormalizedOptionObservation]] = {
        expiry: [] for expiry in selected_expiries
    }
    puts_by_expiry: dict[date, list[NormalizedOptionObservation]] = {
        expiry: [] for expiry in selected_expiries
    }
    observed_spots: set[float] = set()

    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        for raw_row in reader:
            row = _clean_row(raw_row)
            try:
                quote_date = _market_date(_required(row, "QUOTE_DATE"))
                expiry = _market_date(_required(row, "EXPIRE_DATE"))
            except (TypeError, ValueError, KeyError):
                exclusions["invalid_or_unparseable_row"] += 1
                continue
            if quote_date != args.quote_date or expiry not in selected_expiries:
                continue

            for right in (OptionRight.CALL, OptionRight.PUT):
                try:
                    quote, underlying = _raw_observations(
                        row,
                        right=right,
                        artifact_hash=artifact_hash,
                        retrieved_at=retrieved_at,
                    )
                    observation = normalize_european_option_midpoint(quote, underlying)
                except QuoteNormalizationError:
                    exclusions["normalization_failure"] += 1
                    continue
                except (TypeError, ValueError, KeyError):
                    exclusions["invalid_or_unparseable_row"] += 1
                    continue

                observed_spots.add(observation.spot)
                if right is OptionRight.CALL:
                    calls_by_expiry[expiry].append(observation)
                else:
                    puts_by_expiry[expiry].append(observation)

                year_fraction = (expiry - args.quote_date).days / 365.0
                forward = observation.spot * exp(
                    (args.rate - args.dividend_yield) * year_fraction
                )
                if not _eligible_otm_side(quote, forward=forward):
                    exclusions["not_selected_otm_side"] += 1
                    continue

                try:
                    numeraire = FlatMoneyMarketNumeraire(
                        reference_date=observation.valuation_date,
                        continuously_compounded_rate=args.rate,
                    )
                    measure = PricingMeasureSemantics(name="Q^N", numeraire=numeraire)
                    problem = BlackScholesImpliedVolatilityProblem(
                        observation=observation,
                        numeraire=numeraire,
                        pricing_measure=measure,
                        continuous_dividend_yield=args.dividend_yield,
                    )
                    result = infer_implied_volatility(
                        problem,
                        BisectionImpliedVolatility(),
                    )
                except InconsistentObservedPrice:
                    exclusions["financial_inconsistency"] += 1
                    continue
                except ImpliedVolatilityNotBracketed:
                    exclusions["volatility_not_bracketed"] += 1
                    continue
                except ImpliedVolatilityConvergenceError:
                    exclusions["solver_failure"] += 1
                    continue
                except InvalidImpliedVolatilityProblem:
                    exclusions["invalid_inverse_problem"] += 1
                    continue

                inferred_by_expiry[expiry].append(_point(result, problem))

    slices: list[dict[str, object]] = []
    for expiry in sorted(selected_expiries):
        points = inferred_by_expiry[expiry]
        points.sort(key=lambda point: float(point["strike"]))
        slices.append(
            {
                "expiry": expiry.isoformat(),
                "days_to_expiry": (expiry - args.quote_date).days,
                "points": points,
                "static_quote_diagnostics": {
                    "calls": _slice_diagnostics(calls_by_expiry[expiry]),
                    "puts": _slice_diagnostics(puts_by_expiry[expiry]),
                },
            }
        )

    return {
        "evidence_kind": "derived Black-Scholes implied-volatility strike/maturity evidence",
        "source": {
            "repository": _SOURCE_REPOSITORY,
            "commit": _SOURCE_COMMIT,
            "path": _SOURCE_PATH,
            "git_blob_sha1": _SOURCE_GIT_BLOB_SHA1,
            "local_artifact_sha256": artifact_hash,
            "license_note": _LICENSE_NOTES,
        },
        "market_snapshot": {
            "quote_date": args.quote_date.isoformat(),
            "underlying": "SPX",
            "observed_spot_values": sorted(observed_spots),
            "selected_expiries": [expiry.isoformat() for expiry in sorted(selected_expiries)],
            "contract_semantics_source": _CONTRACT_SEMANTICS_SOURCE,
            "contract_semantics_enrichment": "SPXW European exercise; PM settlement",
        },
        "model_inputs": {
            "continuously_compounded_rate": args.rate,
            "continuous_dividend_yield": args.dividend_yield,
            "time_basis": "ACT/365F",
            "note": "flat rate/carry are explicit research assumptions, not observations",
        },
        "quote_policy": "positive non-crossed bid/ask midpoint",
        "selection_policy": "OTM puts below model forward; OTM calls at/above forward",
        "raw_rows_redistributed": False,
        "exclusions": dict(sorted(exclusions.items())),
        "slices": slices,
    }


def main() -> None:
    args = _parse_args()
    evidence = derive_evidence(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
