from __future__ import annotations

from dataclasses import replace

import pytest

from qf_platform.application import (
    M2WorkbenchDraft,
    WorkbenchValuationMethod,
    canonical_black_scholes_draft,
    compose_black_scholes_study,
    make_m2_workbench_request,
    run_m2_workbench,
    selected_method,
)
from qf_platform.pricing import CoxRossRubinstein, MonteCarloValuationResult
from qf_platform.sensitivity import BlackScholesSensitivity


def _request(**changes: str):
    composition = compose_black_scholes_study(canonical_black_scholes_draft())
    draft = replace(M2WorkbenchDraft(), **changes)
    return make_m2_workbench_request(composition, draft)


def test_ui2_method_selection_normalizes_concrete_m2_configuration() -> None:
    request = _request(valuation_method="crr", crr_steps="200")

    assert request.config.valuation_method is WorkbenchValuationMethod.CRR
    method = selected_method(request.config)
    assert isinstance(method, CoxRossRubinstein)
    assert method.steps == 200
    assert method.supports(request.composition.problem)
    assert request.config.method_configuration == "steps=200"


def test_ui2_selected_monte_carlo_preserves_rng_configuration() -> None:
    request = _request(
        valuation_method="monte_carlo",
        monte_carlo_paths="5000",
        monte_carlo_seed="1729",
    )

    analysis = run_m2_workbench(request)
    result = analysis.selected_valuation.result

    assert isinstance(result, MonteCarloValuationResult)
    assert result.paths == 5000
    assert result.seed == 1729
    assert result.standard_error > 0.0


def test_ui2_analysis_compares_methods_and_separate_sensitivity_family() -> None:
    analysis = run_m2_workbench(_request(selected_greek="delta"))

    assert len(analysis.valuations) == 3
    analytic = next(
        run
        for run in analysis.valuations
        if run.method is WorkbenchValuationMethod.ANALYTIC
    )
    assert analytic.result is not None
    assert analytic.result.present_value == pytest.approx(
        10.450583572185565,
        abs=2e-13,
    )
    assert len(analysis.crr_convergence) == 6
    assert len(analysis.monte_carlo_convergence) == 4
    assert len(analysis.sensitivities) == 5
    assert len(analysis.greek_curve) == 41
    assert analysis.greek_curve[0].spot > 0.0
    assert analysis.gamma_bump_study


def test_ui2_preserves_explicit_selected_crr_support_boundary() -> None:
    financial_draft = replace(
        canonical_black_scholes_draft(),
        continuously_compounded_rate="0.50",
        annualized_volatility="0.01",
    )
    composition = compose_black_scholes_study(financial_draft)
    request = make_m2_workbench_request(
        composition,
        replace(M2WorkbenchDraft(), valuation_method="crr", crr_steps="1"),
    )

    analysis = run_m2_workbench(request)

    assert not analysis.selected_valuation.supported
    assert analysis.selected_valuation.result is None


def test_ui2_finite_difference_domain_crossing_remains_unsupported() -> None:
    composition = compose_black_scholes_study(
        replace(canonical_black_scholes_draft(), spot="0.05")
    )
    request = make_m2_workbench_request(
        composition,
        replace(
            M2WorkbenchDraft(),
            selected_greek="delta",
            spot_bump="0.1",
        ),
    )

    analysis = run_m2_workbench(request)
    delta = next(
        run
        for run in analysis.sensitivities
        if run.sensitivity is BlackScholesSensitivity.DELTA
    )

    assert delta.analytic_supported
    assert not delta.finite_difference_supported
    assert delta.finite_difference_result is None
