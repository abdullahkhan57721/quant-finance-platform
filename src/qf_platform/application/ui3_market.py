"""Frontend-neutral UI3 orchestration for merged M4 market/inference evidence."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
from enum import StrEnum

from qf_platform.inference import (
    BisectionImpliedVolatility,
    BlackScholesImpliedVolatilityProblem,
    ImpliedVolatilityConvergenceError,
    ImpliedVolatilityNotBracketed,
    ImpliedVolatilityResult,
    InvalidImpliedVolatilityProblem,
    infer_implied_volatility,
)
from qf_platform.market_data import (
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


class MarketObservationStatus(StrEnum):
    """Concrete UI3 lifecycle status for one raw market observation."""

    INFERRED = "inferred"
    NORMALIZATION_REJECTED = "normalization_rejected"
    INFERENCE_FAILED = "inference_failed"


@dataclass(frozen=True, slots=True)
class MarketWorkbenchConfig:
    """Explicit model/inverse-method configuration for one M4 Workbench run."""

    continuously_compounded_rate: float = 0.03
    continuous_dividend_yield: float = 0.01
    minimum_annualized_volatility: float = 0.0
    maximum_annualized_volatility: float = 5.0
    price_tolerance: float = 1.0e-10
    volatility_tolerance: float = 1.0e-10
    max_iterations: int = 200


@dataclass(frozen=True, slots=True)
class MarketObservationOutcome:
    """Raw evidence plus explicit normalization/inference outcome for one quote."""

    raw_quote: RawOptionQuote
    normalized: NormalizedOptionObservation | None
    result: ImpliedVolatilityResult | None
    status: MarketObservationStatus
    diagnostic: str


@dataclass(frozen=True, slots=True)
class MarketSliceEvidence:
    """Existing M4 same-right strike diagnostics for one normalized slice."""

    expiry: date
    right: OptionRight
    diagnostics: OptionSliceDiagnostics


@dataclass(frozen=True, slots=True)
class EmpiricalSmilePoint:
    """One already-derived point from M4's pinned SPX evidence artifact."""

    expiry: date
    days_to_expiry: float
    strike: float
    right: OptionRight
    log_forward_moneyness: float
    annualized_implied_volatility: float
    vega: float
    local_volatility_shift_for_half_spread: float


@dataclass(frozen=True, slots=True)
class EmpiricalSmileEvidence:
    """Pinned M4 derived evidence; intentionally not raw redistributed quote data."""

    source_repository: str
    source_commit: str
    source_path: str
    source_blob_sha1: str
    license_note: str
    quote_date: date
    underlying: str
    observed_spot: float
    continuously_compounded_rate: float
    continuous_dividend_yield: float
    points: tuple[EmpiricalSmilePoint, ...]
    diagnostic_summary: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class MarketWorkbenchAnalysis:
    """Completed M4 observation/inference evidence for the native Workbench."""

    underlying: RawUnderlyingObservation
    outcomes: tuple[MarketObservationOutcome, ...]
    slice_evidence: tuple[MarketSliceEvidence, ...]
    empirical_evidence: EmpiricalSmileEvidence


def run_market_workbench(
    quotes: tuple[RawOptionQuote, ...],
    underlying: RawUnderlyingObservation,
    config: MarketWorkbenchConfig,
) -> MarketWorkbenchAnalysis:
    """Run raw -> normalized -> inverse evidence using only merged M4 APIs."""

    _validate_market_config(config)
    numeraire = FlatMoneyMarketNumeraire(
        reference_date=underlying.provenance.market_date,
        continuously_compounded_rate=config.continuously_compounded_rate,
    )
    pricing_measure = PricingMeasureSemantics(name="Q^N", numeraire=numeraire)
    method = BisectionImpliedVolatility(
        price_tolerance=config.price_tolerance,
        volatility_tolerance=config.volatility_tolerance,
        max_iterations=config.max_iterations,
    )
    outcomes = tuple(
        _analyze_quote(
            quote,
            underlying,
            config,
            numeraire,
            pricing_measure,
            method,
        )
        for quote in quotes
    )
    return MarketWorkbenchAnalysis(
        underlying=underlying,
        outcomes=outcomes,
        slice_evidence=_slice_evidence(outcomes),
        empirical_evidence=canonical_m4_spx_evidence(),
    )


def canonical_m4_market_workbench() -> MarketWorkbenchAnalysis:
    """Run the deterministic M4 synthetic raw-observation example for UI3."""

    provenance = ObservationProvenance(
        provider="synthetic:m4-ci",
        source="repository fixture",
        market_date=date(2026, 1, 2),
        retrieved_at=datetime(2026, 1, 3, 12, tzinfo=UTC),
        raw_artifact_sha256="c" * 64,
        license_notes="synthetic fixture; unrestricted test use",
    )
    underlying = RawUnderlyingObservation(
        underlying_id="SYN",
        value=100.0,
        provenance=provenance,
    )
    quotes = tuple(_synthetic_quote(row, provenance) for row in _SYNTHETIC_ROWS)
    return run_market_workbench(quotes, underlying, MarketWorkbenchConfig())


def canonical_m4_spx_evidence() -> EmpiricalSmileEvidence:
    """Return M4's pinned derived SPX evidence without claiming raw-row ownership."""

    return EmpiricalSmileEvidence(
        source_repository="IceCurrent/local_volatility_model",
        source_commit="428531599bf3945f5d51691fdd21b1667eb14958",
        source_path="data/data.csv",
        source_blob_sha1="8d1db0f2710c4707555c8263f9b7f8f527974836",
        license_note=(
            "No repository license file was present when M4 evidence was produced; "
            "raw rows are not redistributed here."
        ),
        quote_date=date(2023, 1, 4),
        underlying="SPX",
        observed_spot=3853.39,
        continuously_compounded_rate=0.045,
        continuous_dividend_yield=0.017,
        points=_EMPIRICAL_SPX_POINTS,
        diagnostic_summary=(
            "One constant Black-Scholes volatility cannot reconcile the selected option set.",
            "Both expiries show materially decreasing implied volatility as strike rises.",
            "Implied-volatility levels also differ across maturity.",
            "Same-right midpoint slices were monotone in strike but contained discrete convexity violations; M4 records rather than repairs them.",
        ),
    )


def _analyze_quote(
    quote: RawOptionQuote,
    underlying: RawUnderlyingObservation,
    config: MarketWorkbenchConfig,
    numeraire: FlatMoneyMarketNumeraire,
    pricing_measure: PricingMeasureSemantics[date],
    method: BisectionImpliedVolatility,
) -> MarketObservationOutcome:
    try:
        normalized = normalize_european_option_midpoint(quote, underlying)
    except QuoteNormalizationError as exc:
        return MarketObservationOutcome(
            raw_quote=quote,
            normalized=None,
            result=None,
            status=MarketObservationStatus.NORMALIZATION_REJECTED,
            diagnostic=str(exc),
        )

    try:
        problem = BlackScholesImpliedVolatilityProblem(
            observation=normalized,
            numeraire=numeraire,
            pricing_measure=pricing_measure,
            continuous_dividend_yield=config.continuous_dividend_yield,
            minimum_annualized_volatility=config.minimum_annualized_volatility,
            maximum_annualized_volatility=config.maximum_annualized_volatility,
        )
        result = infer_implied_volatility(problem, method)
    except (
        InvalidImpliedVolatilityProblem,
        ImpliedVolatilityNotBracketed,
        ImpliedVolatilityConvergenceError,
    ) as exc:
        return MarketObservationOutcome(
            raw_quote=quote,
            normalized=normalized,
            result=None,
            status=MarketObservationStatus.INFERENCE_FAILED,
            diagnostic=f"{type(exc).__name__}: {exc}",
        )

    return MarketObservationOutcome(
        raw_quote=quote,
        normalized=normalized,
        result=result,
        status=MarketObservationStatus.INFERRED,
        diagnostic="Normalized and inferred through the merged M4 pipeline.",
    )


def _slice_evidence(
    outcomes: tuple[MarketObservationOutcome, ...],
) -> tuple[MarketSliceEvidence, ...]:
    grouped: dict[tuple[date, OptionRight], list[NormalizedOptionObservation]] = {}
    for outcome in outcomes:
        normalized = outcome.normalized
        if normalized is None:
            continue
        key = (outcome.raw_quote.expiry, outcome.raw_quote.right)
        grouped.setdefault(key, []).append(normalized)

    evidence: list[MarketSliceEvidence] = []
    for (expiry, right), observations in sorted(
        grouped.items(),
        key=lambda item: (item[0][0], item[0][1].value),
    ):
        if len(observations) < 2:
            continue
        evidence.append(
            MarketSliceEvidence(
                expiry=expiry,
                right=right,
                diagnostics=diagnose_option_strike_slice(observations),
            )
        )
    return tuple(evidence)


def _validate_market_config(config: MarketWorkbenchConfig) -> None:
    if config.maximum_annualized_volatility <= config.minimum_annualized_volatility:
        raise ValueError("maximum volatility must exceed minimum volatility")
    if config.minimum_annualized_volatility < 0.0:
        raise ValueError("minimum volatility must be non-negative")
    if config.price_tolerance <= 0.0 or config.volatility_tolerance <= 0.0:
        raise ValueError("inverse tolerances must be positive")
    if config.max_iterations <= 0:
        raise ValueError("max_iterations must be positive")


@dataclass(frozen=True, slots=True)
class _SyntheticRow:
    contract_id: str
    expiry: date
    strike: float
    right: OptionRight
    bid: float
    ask: float


def _synthetic_quote(
    row: _SyntheticRow,
    provenance: ObservationProvenance,
) -> RawOptionQuote:
    return RawOptionQuote(
        contract_id=row.contract_id,
        underlying_id="SYN",
        expiry=row.expiry,
        strike=row.strike,
        right=row.right,
        exercise_style=OptionExerciseStyle.EUROPEAN,
        provenance=provenance,
        bid=row.bid,
        ask=row.ask,
        settlement_time=OptionSettlementTime.PM,
    )


_SYNTHETIC_ROWS = (
    _SyntheticRow(
        "SYN-20260402-P-80",
        date(2026, 4, 2),
        80.0,
        OptionRight.PUT,
        0.3511730806957949,
        0.3711730806957949,
    ),
    _SyntheticRow(
        "SYN-20260402-P-90",
        date(2026, 4, 2),
        90.0,
        OptionRight.PUT,
        1.44971364813132,
        1.46971364813132,
    ),
    _SyntheticRow(
        "SYN-20260402-P-100",
        date(2026, 4, 2),
        100.0,
        OptionRight.PUT,
        4.476912169390138,
        4.496912169390138,
    ),
    _SyntheticRow(
        "SYN-20260402-C-110",
        date(2026, 4, 2),
        110.0,
        OptionRight.CALL,
        1.294607271324123,
        1.314607271324123,
    ),
    _SyntheticRow(
        "SYN-20260402-C-120",
        date(2026, 4, 2),
        120.0,
        OptionRight.CALL,
        0.1970973700882357,
        0.2170973700882357,
    ),
    _SyntheticRow(
        "SYN-20260701-P-80",
        date(2026, 7, 1),
        80.0,
        OptionRight.PUT,
        0.994161150392397,
        1.014161150392397,
    ),
    _SyntheticRow(
        "SYN-20260701-P-90",
        date(2026, 7, 1),
        90.0,
        OptionRight.PUT,
        2.626344787547415,
        2.646344787547415,
    ),
    _SyntheticRow(
        "SYN-20260701-P-100",
        date(2026, 7, 1),
        100.0,
        OptionRight.PUT,
        6.025026134139123,
        6.045026134139123,
    ),
    _SyntheticRow(
        "SYN-20260701-C-110",
        date(2026, 7, 1),
        110.0,
        OptionRight.CALL,
        2.904109786167252,
        2.924109786167252,
    ),
    _SyntheticRow(
        "SYN-20260701-C-120",
        date(2026, 7, 1),
        120.0,
        OptionRight.CALL,
        0.9434232912587033,
        0.9634232912587033,
    ),
)


_EMPIRICAL_SPX_POINTS = (
    EmpiricalSmilePoint(
        date(2023, 2, 3),
        30.0,
        3720.0,
        OptionRight.PUT,
        -0.037530981928,
        0.230315263038,
        367.298111465861,
        0.000680646026,
    ),
    EmpiricalSmilePoint(
        date(2023, 2, 3),
        30.0,
        3800.0,
        OptionRight.PUT,
        -0.016253583481,
        0.220762212996,
        422.174971401069,
        0.002605554745,
    ),
    EmpiricalSmilePoint(
        date(2023, 2, 3),
        30.0,
        3850.0,
        OptionRight.PUT,
        -0.003181501914,
        0.214492740344,
        438.614532250333,
        0.000797967177,
    ),
    EmpiricalSmilePoint(
        date(2023, 2, 3),
        30.0,
        3870.0,
        OptionRight.CALL,
        0.001999856828,
        0.209316325619,
        440.106729403633,
        0.000681652835,
    ),
    EmpiricalSmilePoint(
        date(2023, 2, 3),
        30.0,
        3900.0,
        OptionRight.CALL,
        0.009721902922,
        0.206511411283,
        436.140100667848,
        0.002866051524,
    ),
    EmpiricalSmilePoint(
        date(2023, 2, 3),
        30.0,
        3970.0,
        OptionRight.CALL,
        0.027511444486,
        0.196228319381,
        395.759466446703,
        0.000631696829,
    ),
    EmpiricalSmilePoint(
        date(2023, 2, 3),
        30.0,
        4020.0,
        OptionRight.CALL,
        0.040027252418,
        0.190770906584,
        343.384635970668,
        0.001019265172,
    ),
    EmpiricalSmilePoint(
        date(2023, 4, 28),
        113.96,
        3720.0,
        OptionRight.PUT,
        -0.043971749052,
        0.231224804687,
        787.174674138685,
        0.000635183037,
    ),
    EmpiricalSmilePoint(
        date(2023, 4, 28),
        113.96,
        3800.0,
        OptionRight.PUT,
        -0.022694350604,
        0.223681235911,
        829.358585637301,
        0.00054258798,
    ),
    EmpiricalSmilePoint(
        date(2023, 4, 28),
        113.96,
        3900.0,
        OptionRight.CALL,
        0.003281135799,
        0.214866346878,
        853.975671595706,
        0.00064404645,
    ),
    EmpiricalSmilePoint(
        date(2023, 4, 28),
        113.96,
        3950.0,
        OptionRight.CALL,
        0.016020161576,
        0.209757818695,
        851.831728640195,
        0.000586970388,
    ),
    EmpiricalSmilePoint(
        date(2023, 4, 28),
        113.96,
        4075.0,
        OptionRight.CALL,
        0.047175329356,
        0.196322125092,
        796.359430556647,
        0.000565071477,
    ),
    EmpiricalSmilePoint(
        date(2023, 4, 28),
        113.96,
        4110.0,
        OptionRight.CALL,
        0.055727611171,
        0.193347267542,
        768.011241281436,
        0.002213509267,
    ),
    EmpiricalSmilePoint(
        date(2023, 4, 28),
        113.96,
        4240.0,
        OptionRight.CALL,
        0.086867851907,
        0.182245070744,
        619.38656300988,
        0.000565075223,
    ),
)
