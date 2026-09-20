"""F4 browser-service traceability tests."""

from __future__ import annotations

from qf_platform.web.services import (
    HedgingInputs,
    ValuationInputs,
    load_m6_market_reference_service,
    load_market_service,
    load_performance_service,
    load_validation_service,
    run_hedging_service,
    run_heston_calibration_service,
    run_heston_pricing_service,
    run_valuation_service,
)


def _require_value(result):
    assert result.error is None
    assert result.value is not None
    return result.value


def test_valuation_service_uses_existing_m2_evidence() -> None:
    presentation = _require_value(run_valuation_service())
    assert {row.method for row in presentation.valuation_rows} == {
        "Black-Scholes analytic",
        "Cox-Ross-Rubinstein",
        "Monte Carlo",
    }
    assert {row.greek for row in presentation.greek_rows} == {
        "Delta",
        "Gamma",
        "Vega",
        "Theta",
        "Rho",
    }

    invalid = run_valuation_service(ValuationInputs(spot="not-a-number"))
    assert invalid.value is None
    assert invalid.error == "spot must be a number"


def test_hedging_service_preserves_model_generated_non_backtest_evidence() -> None:
    presentation = _require_value(
        run_hedging_service(
            HedgingInputs(
                generating_volatility="0.30",
                hedging_volatility="0.20",
                replicate_count="4",
                transaction_cost_rate="0.001",
            )
        )
    )
    assert presentation.frequency_rows
    assert presentation.replicate_error_plot.series
    joined = " ".join(row.detail for row in presentation.provenance_rows).lower()
    assert "rng" in joined or "seed" in joined


def test_market_and_heston_services_return_existing_presentations() -> None:
    market = _require_value(load_market_service())
    assert market.empirical_smile_plot.series
    assert market.empirical_provenance_rows

    pricing = _require_value(run_heston_pricing_service())
    assert pricing.method_comparison_plot.series
    assert pricing.fourier_stability_plot.series

    calibration = _require_value(run_heston_calibration_service("thin"))
    assert calibration.conditioning_rows
    assert calibration.objective_plot.series

    recorded_market = _require_value(load_m6_market_reference_service())
    assert recorded_market.provenance_rows
    assert recorded_market.conditioning_rows


def test_validation_and_performance_services_preserve_bounded_evidence() -> None:
    validation = _require_value(load_validation_service())
    assert validation.evaluation_metric_rows
    assert validation.model_risk_rows
    risk_text = " ".join(
        f"{row.label} {row.value} {row.detail}" for row in validation.model_risk_rows
    ).lower()
    assert "temporal" in risk_text
    assert "hedging" in risk_text

    performance = _require_value(load_performance_service())
    assert performance.workload_rows
    assert performance.native_decision_rows
    assert performance.runtime_plot.series
