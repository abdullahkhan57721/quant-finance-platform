"""Concrete tabular adapter for M4 market and implied-volatility evidence."""

from __future__ import annotations

from qf_platform.application import MarketWorkbenchAnalysis, MarketWorkbenchConfig

from .model import ReportColumn, ReportField, ReportTable, TabularReport


def market_iv_report(
    config: MarketWorkbenchConfig,
    analysis: MarketWorkbenchAnalysis,
) -> TabularReport:
    """Preserve raw/normalized/inferred distinctions in exported M4 evidence."""

    provenance = analysis.underlying.provenance
    outcome_rows = []
    for outcome in analysis.outcomes:
        quote = outcome.raw_quote
        normalized = outcome.normalized
        result = outcome.result
        outcome_rows.append(
            (
                quote.contract_id,
                quote.expiry.isoformat(),
                quote.strike,
                quote.right.value,
                quote.bid,
                quote.ask,
                normalized.target_price if normalized is not None else None,
                normalized.normalization_version if normalized is not None else None,
                result.annualized_volatility if result is not None else None,
                result.model_price if result is not None else None,
                result.residual if result is not None else None,
                result.vega if result is not None else None,
                (
                    result.local_volatility_shift_for_half_spread
                    if result is not None
                    else None
                ),
                outcome.status.value,
                outcome.diagnostic,
            )
        )

    empirical = analysis.empirical_evidence
    return TabularReport(
        report_id="market_implied_volatility",
        title="Option observations and Black-Scholes implied-volatility evidence",
        metadata=(
            ReportField("underlying_id", analysis.underlying.underlying_id),
            ReportField("observed_spot", analysis.underlying.value, "spot units"),
            ReportField("provider", provenance.provider),
            ReportField("source", provenance.source),
            ReportField("market_date", provenance.market_date.isoformat()),
            ReportField("retrieved_at", provenance.retrieved_at.isoformat()),
            ReportField("license_notes", provenance.license_notes),
            ReportField(
                "continuously_compounded_rate",
                config.continuously_compounded_rate,
                "annual decimal",
            ),
            ReportField(
                "continuous_dividend_yield",
                config.continuous_dividend_yield,
                "annual decimal",
            ),
            ReportField("quote_normalization", "explicit European PM midpoint"),
            ReportField(\n                "inverse_method", "Black-Scholes implied volatility by bisection"\n            ),
        ),
        tables=(
            ReportTable(
                "observations",
                (
                    ReportColumn("contract_id", "Contract ID"),
                    ReportColumn("expiry", "Expiry"),
                    ReportColumn("strike", "Strike", "spot units"),
                    ReportColumn("right", "Right"),
                    ReportColumn("raw_bid", "Raw bid", "price units"),
                    ReportColumn("raw_ask", "Raw ask", "price units"),
                    ReportColumn(
                        "normalized_target",
                        "Normalized target",
                        "price units",
                    ),
                    ReportColumn("normalization_version", "Normalization version"),
                    ReportColumn(
                        "implied_vol",
                        "Implied volatility",
                        "annual decimal",
                    ),
                    ReportColumn("model_price", "Model price", "price units"),
                    ReportColumn("residual", "Model - target", "price units"),
                    ReportColumn("vega", "Vega", "native M2 vega units"),
                    ReportColumn(
                        "half_spread_vol_shift",
                        "Local volatility shift for half spread",
                        "annual volatility decimal",
                    ),
                    ReportColumn("status", "Status"),
                    ReportColumn("diagnostic", "Diagnostic"),
                ),
                tuple(outcome_rows),
            ),
            ReportTable(
                "derived_spx_smile",
                (
                    ReportColumn("expiry", "Expiry"),
                    ReportColumn("days_to_expiry", "Days to expiry", "days"),
                    ReportColumn("strike", "Strike", "spot units"),
                    ReportColumn("right", "Right"),
                    ReportColumn(
                        "log_forward_moneyness",
                        "Log forward moneyness",
                    ),
                    ReportColumn(
                        "implied_vol",
                        "Implied volatility",
                        "annual decimal",
                    ),
                    ReportColumn("vega", "Vega", "native M2 vega units"),
                    ReportColumn(
                        "half_spread_vol_shift",
                        "Local volatility shift for half spread",
                        "annual volatility decimal",
                    ),
                ),
                tuple(
                    (
                        point.expiry.isoformat(),
                        point.days_to_expiry,
                        point.strike,
                        point.right.value,
                        point.log_forward_moneyness,
                        point.annualized_implied_volatility,
                        point.vega,
                        point.local_volatility_shift_for_half_spread,
                    )
                    for point in empirical.points
                ),
            ),
            ReportTable(
                "spx_provenance",
                (
                    ReportColumn("field", "Field"),
                    ReportColumn("value", "Value"),
                ),
                (
                    ("source_repository", empirical.source_repository),
                    ("source_commit", empirical.source_commit),
                    ("source_path", empirical.source_path),
                    ("source_blob_sha1", empirical.source_blob_sha1),
                    ("license_note", empirical.license_note),
                    ("quote_date", empirical.quote_date.isoformat()),
                    ("underlying", empirical.underlying),
                ),
            ),
        ),
    )
