"""Renderer-neutral UI3 presentation for merged M4 market/inference evidence."""

from __future__ import annotations

from dataclasses import dataclass

from qf_platform.application.ui3_market import (
    EmpiricalSmileEvidence,
    MarketObservationOutcome,
    MarketObservationStatus,
    MarketWorkbenchAnalysis,
)
from qf_platform.presentation.black_scholes import PresentationRow
from qf_platform.presentation.plotting import PlotData, PlotPoint, PlotSeries


@dataclass(frozen=True, slots=True)
class MarketObservationRow:
    """One native-table row retaining raw, normalized, and inferred distinctions."""

    contract_id: str
    expiry: str
    strike: str
    right: str
    bid: str
    ask: str
    normalized_price: str
    observed_spot: str
    implied_volatility: str
    status: str
    diagnostic: str


@dataclass(frozen=True, slots=True)
class MarketObservationDetail:
    """Concrete read-only inspector values for one selected observation."""

    table_row: MarketObservationRow
    provenance_rows: tuple[PresentationRow, ...]
    inverse_rows: tuple[PresentationRow, ...]
    inspector_rows: tuple[PresentationRow, ...]


@dataclass(frozen=True, slots=True)
class MarketWorkbenchPresentation:
    """Concrete UI3 M4 presentation, including synthetic and empirical evidence."""

    observation_details: tuple[MarketObservationDetail, ...]
    diagnostic_rows: tuple[PresentationRow, ...]
    empirical_provenance_rows: tuple[PresentationRow, ...]
    empirical_summary_rows: tuple[PresentationRow, ...]
    synthetic_smile_plot: PlotData
    synthetic_conditioning_plot: PlotData
    empirical_smile_plot: PlotData
    empirical_conditioning_plot: PlotData



def build_market_workbench_presentation(
    analysis: MarketWorkbenchAnalysis,
) -> MarketWorkbenchPresentation:
    """Convert immutable M4 evidence into curated renderer-neutral values."""

    return MarketWorkbenchPresentation(
        observation_details=tuple(
            _observation_detail(outcome) for outcome in analysis.outcomes
        ),
        diagnostic_rows=_diagnostic_rows(analysis),
        empirical_provenance_rows=_empirical_provenance_rows(
            analysis.empirical_evidence
        ),
        empirical_summary_rows=tuple(
            PresentationRow(
                f"M4 empirical finding {index + 1}",
                text,
                "Derived SPX evidence; no smoothing or surface repair is applied.",
                "Derived evidence",
            )
            for index, text in enumerate(
                analysis.empirical_evidence.diagnostic_summary
            )
        ),
        synthetic_smile_plot=_synthetic_smile_plot(analysis),
        synthetic_conditioning_plot=_synthetic_conditioning_plot(analysis),
        empirical_smile_plot=_empirical_smile_plot(analysis.empirical_evidence),
        empirical_conditioning_plot=_empirical_conditioning_plot(
            analysis.empirical_evidence
        ),
    )


def _observation_detail(outcome: MarketObservationOutcome) -> MarketObservationDetail:
    quote = outcome.raw_quote
    provenance = quote.provenance
    normalized = outcome.normalized
    result = outcome.result
    row = MarketObservationRow(
        contract_id=quote.contract_id,
        expiry=quote.expiry.isoformat(),
        strike=_number(quote.strike),
        right=quote.right.value.title(),
        bid=_optional_number(quote.bid),
        ask=_optional_number(quote.ask),
        normalized_price=(
            "—" if normalized is None else _number(normalized.target_price)
        ),
        observed_spot=(
            "—" if normalized is None else _number(normalized.spot)
        ),
        implied_volatility=(
            "—" if result is None else _percent(result.annualized_volatility)
        ),
        status=_status_label(outcome.status),
        diagnostic=outcome.diagnostic,
    )
    provenance_rows = (
        PresentationRow("Raw contract id", quote.contract_id, "Immutable raw observation identity.", "Raw"),
        PresentationRow("Provider", provenance.provider, provenance.source, "Raw provenance"),
        PresentationRow("Market date", provenance.market_date.isoformat(), "Historical/as-of date carried by the raw evidence.", "Raw provenance"),
        PresentationRow("Retrieved at", provenance.retrieved_at.isoformat(), "Timezone-aware retrieval timestamp.", "Raw provenance"),
        PresentationRow("Observed at", "—" if provenance.observed_at is None else provenance.observed_at.isoformat(), "May be absent when the source lacks contract-level timestamps.", "Raw provenance"),
        PresentationRow("Raw artifact SHA-256", provenance.raw_artifact_sha256 or "—", "Source artifact identity when available.", "Raw provenance"),
        PresentationRow("License / redistribution note", provenance.license_notes, "Preserved source-use context.", "Raw provenance"),
        PresentationRow("Normalization", "Rejected" if normalized is None else normalized.normalization_version, outcome.diagnostic, "Normalization"),
    )
    inverse_rows = _inverse_rows(outcome)
    inspector_rows = _inverse_inspector(outcome)
    return MarketObservationDetail(row, provenance_rows, inverse_rows, inspector_rows)


def _inverse_rows(outcome: MarketObservationOutcome) -> tuple[PresentationRow, ...]:
    normalized = outcome.normalized
    result = outcome.result
    if normalized is None:
        return (
            PresentationRow(
                "Inverse problem",
                "Not formed",
                outcome.diagnostic,
                "Normalization rejected",
            ),
        )
    if result is None:
        return (
            PresentationRow("Observed target", _number(normalized.target_price), "Normalized bid/ask midpoint.", "Observed"),
            PresentationRow("Inverse result", "Unresolved", outcome.diagnostic, "Inference failed"),
        )
    return (
        PresentationRow("Observed target", _number(result.target_price), "Normalized observed price; not a model-generated price.", "Observed"),
        PresentationRow("Implied volatility", _percent(result.annualized_volatility), "Annualized decimal volatility solving the M4 inverse problem.", "Inferred"),
        PresentationRow("Model price", _number(result.model_price), "Forward Black-Scholes price at the inferred volatility.", "Modeled"),
        PresentationRow("Residual", _number(result.residual), "Model price minus observed target at termination.", "Numerical evidence"),
        PresentationRow("Iterations / evaluations", f"{result.iterations} / {result.function_evaluations}", "Bisection iteration and model-price evaluation counts.", "Solver evidence"),
        PresentationRow("Vega at solution", _optional_number(result.vega), "M2 analytic Vega retained as local conditioning evidence.", "Conditioning"),
        PresentationRow("dVol / dPrice", _optional_number(result.volatility_change_per_price_unit), "Local inverse price-to-volatility sensitivity, approximately 1/Vega.", "Conditioning"),
        PresentationRow("Half-spread IV shift", _optional_percent(result.local_volatility_shift_for_half_spread), "First-order volatility shift induced by half the observed bid/ask spread.", "Conditioning"),
    )


def _inverse_inspector(outcome: MarketObservationOutcome) -> tuple[PresentationRow, ...]:
    normalized = outcome.normalized
    result = outcome.result
    return (
        PresentationRow("Observed target", "Unavailable" if normalized is None else _number(normalized.target_price), "Historical/synthetic observation after explicit midpoint normalization.", "M4 observation"),
        PresentationRow("Forward model", "Black-Scholes European option pricing", "Forward direction maps volatility to a model price.", "M1/M4"),
        PresentationRow("Unknown parameter", "Annualized volatility sigma", "Inverse direction asks which sigma reconciles the observed target.", "M4 inverse"),
        PresentationRow("Admissible domain", "[0, 5] annualized decimal volatility", "Canonical UI3 M4 example; financial price bounds are checked before solving.", "M4 inverse"),
        PresentationRow("Inverse method", "Bracketed bisection", "Root finder is the numerical method, not the inverse financial problem.", "M4 method"),
        PresentationRow("Conditioning evidence", "Unavailable" if result is None else f"Vega={_optional_number(result.vega)}; dVol/dPrice={_optional_number(result.volatility_change_per_price_unit)}", "Root convergence and local conditioning remain separate claims.", "M4 evidence"),
    )


def _diagnostic_rows(analysis: MarketWorkbenchAnalysis) -> tuple[PresentationRow, ...]:
    rows: list[PresentationRow] = []
    for item in analysis.slice_evidence:
        diagnostics = item.diagnostics
        rows.append(
            PresentationRow(
                f"{item.expiry.isoformat()} {item.right.value} strike slice",
                "Passes checked conditions" if diagnostics.passes else "Observed violations",
                (
                    f"monotonicity={len(diagnostics.monotonicity_violations)}; "
                    f"convexity={len(diagnostics.convexity_violations)}; "
                    f"strikes={', '.join(f'{strike:g}' for strike in diagnostics.strikes)}"
                ),
                "Diagnostic only — no repair",
            )
        )
    return tuple(rows)


def _empirical_provenance_rows(
    evidence: EmpiricalSmileEvidence,
) -> tuple[PresentationRow, ...]:
    return (
        PresentationRow("Evidence kind", "Derived Black-Scholes implied-volatility strike/maturity evidence", "No raw option rows are redistributed in UI3.", "Empirical derived"),
        PresentationRow("Source repository", evidence.source_repository, f"commit {evidence.source_commit}; {evidence.source_path}", "External source"),
        PresentationRow("Source blob SHA-1", evidence.source_blob_sha1, "Pinned upstream data-object identity used by M4.", "Provenance"),
        PresentationRow("Quote date / underlying", f"{evidence.quote_date.isoformat()} / {evidence.underlying}", f"observed spot={evidence.observed_spot:g}", "Historical evidence"),
        PresentationRow("Model assumptions", f"r={evidence.continuously_compounded_rate:g}; q={evidence.continuous_dividend_yield:g}; ACT/365F", "Rate/carry are explicit research assumptions, not inferred observations.", "Derived evidence"),
        PresentationRow("License note", evidence.license_note, "UI3 therefore renders only the derived M4 evidence points.", "Non-redistribution"),
    )


def _synthetic_smile_plot(analysis: MarketWorkbenchAnalysis) -> PlotData:
    grouped: dict[str, list[PlotPoint]] = {}
    for outcome in analysis.outcomes:
        if outcome.result is None:
            continue
        key = outcome.raw_quote.expiry.isoformat()
        grouped.setdefault(key, []).append(
            PlotPoint(outcome.raw_quote.strike, outcome.result.annualized_volatility)
        )
    return PlotData(
        "Synthetic M4 implied volatility by strike",
        "Strike",
        "Annualized implied volatility",
        tuple(
            PlotSeries(expiry, expiry, tuple(sorted(points, key=lambda point: point.x)))
            for expiry, points in sorted(grouped.items())
        ),
    )


def _synthetic_conditioning_plot(analysis: MarketWorkbenchAnalysis) -> PlotData:
    grouped: dict[str, list[PlotPoint]] = {}
    for outcome in analysis.outcomes:
        result = outcome.result
        if result is None or result.local_volatility_shift_for_half_spread is None:
            continue
        key = outcome.raw_quote.expiry.isoformat()
        grouped.setdefault(key, []).append(
            PlotPoint(
                outcome.raw_quote.strike,
                result.local_volatility_shift_for_half_spread,
            )
        )
    return PlotData(
        "Synthetic quote-width conditioning",
        "Strike",
        "Half-spread implied-volatility shift",
        tuple(
            PlotSeries(expiry, expiry, tuple(sorted(points, key=lambda point: point.x)))
            for expiry, points in sorted(grouped.items())
        ),
    )


def _empirical_smile_plot(evidence: EmpiricalSmileEvidence) -> PlotData:
    grouped: dict[str, list[PlotPoint]] = {}
    for point in evidence.points:
        key = point.expiry.isoformat()
        grouped.setdefault(key, []).append(
            PlotPoint(point.strike, point.annualized_implied_volatility)
        )
    return PlotData(
        "Pinned M4 SPX implied-volatility strike slices",
        "Strike",
        "Annualized implied volatility",
        tuple(
            PlotSeries(expiry, expiry, tuple(sorted(points, key=lambda item: item.x)))
            for expiry, points in sorted(grouped.items())
        ),
    )


def _empirical_conditioning_plot(evidence: EmpiricalSmileEvidence) -> PlotData:
    grouped: dict[str, list[PlotPoint]] = {}
    for point in evidence.points:
        key = point.expiry.isoformat()
        grouped.setdefault(key, []).append(
            PlotPoint(point.strike, point.local_volatility_shift_for_half_spread)
        )
    return PlotData(
        "Pinned M4 SPX quote-width conditioning",
        "Strike",
        "Half-spread implied-volatility shift",
        tuple(
            PlotSeries(expiry, expiry, tuple(sorted(points, key=lambda item: item.x)))
            for expiry, points in sorted(grouped.items())
        ),
    )


def _status_label(status: MarketObservationStatus) -> str:
    if status is MarketObservationStatus.INFERRED:
        return "Normalized + inferred"
    if status is MarketObservationStatus.NORMALIZATION_REJECTED:
        return "Normalization rejected"
    return "Inference failed"


def _number(value: float) -> str:
    return f"{value:.10g}"


def _optional_number(value: float | None) -> str:
    return "—" if value is None else _number(value)


def _percent(value: float) -> str:
    return f"{100.0 * value:.6g}%"


def _optional_percent(value: float | None) -> str:
    return "—" if value is None else _percent(value)
