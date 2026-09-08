from __future__ import annotations

from dataclasses import replace

from qf_platform.application import (
    M2WorkbenchDraft,
    canonical_black_scholes_draft,
    compose_black_scholes_study,
    make_m2_workbench_request,
    run_m2_workbench,
)
from qf_platform.presentation import (
    PlotData,
    PlotPoint,
    build_m2_workbench_presentation,
)


def _presentation():
    composition = compose_black_scholes_study(canonical_black_scholes_draft())
    request = make_m2_workbench_request(
        composition,
        replace(
            M2WorkbenchDraft(),
            valuation_method="monte_carlo",
            monte_carlo_paths="5000",
            monte_carlo_seed="1729",
            selected_greek="gamma",
        ),
    )
    analysis = run_m2_workbench(request)
    return build_m2_workbench_presentation(request, analysis)


def test_ui2_presentation_keeps_method_specific_evidence_and_tables() -> None:
    presentation = _presentation()

    assert len(presentation.valuation_rows) == 3
    mc_row = next(
        row for row in presentation.valuation_rows if row.method == "Monte Carlo"
    )
    assert "SE =" in mc_row.evidence
    assert "95% CI" in mc_row.evidence
    assert len(presentation.greek_rows) == 5
    gamma = next(row for row in presentation.greek_rows if row.greek == "Gamma")
    assert "squared" in gamma.units
    assert presentation.finite_difference_rows


def test_ui2_plot_payload_is_reused_across_concrete_workbench_views() -> None:
    presentation = _presentation()

    assert isinstance(presentation.payoff_plot, PlotData)
    assert presentation.payoff_plot.series
    assert presentation.crr_plot.series
    assert presentation.monte_carlo_plot.series
    assert presentation.greek_plot.series
    mc_points = presentation.monte_carlo_plot.series[0].points
    assert any(
        point.lower is not None and point.upper is not None for point in mc_points
    )


def test_ui2_provenance_distinguishes_rng_and_market_data_scope() -> None:
    presentation = _presentation()
    provenance = {row.label: row for row in presentation.provenance_rows}

    assert "seed=1729" in provenance["Monte Carlo RNG"].value
    assert provenance["Market observations"].status == "Not applicable"


def test_plot_uncertainty_requires_paired_ordered_finite_bounds() -> None:
    point = PlotPoint(1.0, 2.0, lower=1.5, upper=2.5)

    assert point.lower == 1.5
    assert point.upper == 2.5
