from __future__ import annotations

from qf_platform.application import (
    HestonCalibrationDraft,
    HestonPricingDraft,
    canonical_m6_market_reference,
    make_heston_calibration_request,
    make_heston_pricing_request,
    run_heston_calibration,
    run_heston_pricing,
)
from qf_platform.presentation import (
    build_heston_calibration_presentation,
    build_heston_pricing_presentation,
    build_m6_market_reference_presentation,
)


def test_heston_pricing_presentation_teaches_model_method_and_uncertainty_boundaries() -> (
    None
):
    request = make_heston_pricing_request(
        HestonPricingDraft(
            fourier_intervals="64",
            monte_carlo_paths="256",
            monte_carlo_time_steps="16",
            monte_carlo_seed="23",
        )
    )
    presentation = build_heston_pricing_presentation(
        request,
        run_heston_pricing(request),
    )

    assert any(
        row.label == "Selected Heston composition" and "(S_t, v_t)" in row.value
        for row in presentation.model_rows
    )
    assert any(row.label == "Feller diagnostic" for row in presentation.parameter_rows)
    assert any(
        row.label == "No path display" and row.status == "Intentional"
        for row in presentation.result_rows
    )
    assert presentation.method_comparison_plot.series[1].points[0].lower is not None
    assert "Fourier" in presentation.fourier_rows[0].value
    assert "Monte Carlo" in presentation.monte_carlo_rows[0].value


def test_thin_calibration_presentation_makes_identifiability_first_class() -> None:
    analysis = run_heston_calibration(
        make_heston_calibration_request(
            "thin",
            HestonCalibrationDraft(fourier_intervals="64"),
        )
    )
    presentation = build_heston_calibration_presentation(analysis)

    assert any(
        row.label == "Target space" and row.value == "Option price"
        for row in presentation.problem_rows
    )
    assert all(row.status == "Rank deficient" for row in presentation.run_rows)
    assert any(
        row.label == "Interpretation"
        and "Tiny fit loss" in row.value
        and "identified structural parameter" in row.detail
        for row in presentation.conditioning_rows
    )
    assert any(
        row.label == "Progress stream" and row.status == "Intentional"
        for row in presentation.inspector_rows
    )


def test_real_market_reference_presentation_preserves_provenance_and_nonclaims() -> (
    None
):
    presentation = build_m6_market_reference_presentation(
        canonical_m6_market_reference()
    )

    assert any(
        row.label == "Pinned public source" for row in presentation.provenance_rows
    )
    assert len(presentation.start_rows) == 3
    assert any(
        row.label == "Scientific interpretation"
        and "M7" in row.detail
        and row.status == "Do not over-interpret"
        for row in presentation.conditioning_rows
    )
    assert len(presentation.residual_plot.series[0].points) == 14
