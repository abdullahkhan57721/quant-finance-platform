from __future__ import annotations

import pytest

from qf_platform.application import (
    canonical_black_scholes_draft,
    compose_black_scholes_study,
)
from qf_platform.presentation import build_black_scholes_presentation
from qf_platform.pricing import evaluate


def test_presentation_consumes_authoritative_m1_result_and_contract_payoff() -> None:
    composition = compose_black_scholes_study(canonical_black_scholes_draft())
    result = evaluate(composition.problem, composition.method)
    presentation = build_black_scholes_presentation(composition, result)

    assert result.present_value == pytest.approx(10.450583572185565, abs=2e-13)
    assert presentation.payoff_points[0].underlying == 0.0
    assert presentation.payoff_points[0].payoff == 0.0
    assert presentation.payoff_points[-1].underlying == 200.0
    assert presentation.payoff_points[-1].payoff == 100.0

    inspector = {row.label: row for row in presentation.inspector_rows}
    assert inspector["State"].value == "Spot = 100"
    assert inspector["Pricing measure"].value == "Q^B"
    assert inspector["Valuation method"].status == "Supported"

    evidence = {row.label: row for row in presentation.evidence_rows}
    assert evidence["Put-call parity"].status == "Reference evidence"
    assert "displayed parity residual" in evidence["Put-call parity"].detail
    assert evidence["Discounted no-arbitrage bounds"].status == "Pass"
    assert evidence["Authoritative valuation result"].value.startswith("PV = 10.45058")


def test_presentation_has_no_qt_dependency() -> None:
    import qf_platform.presentation.black_scholes as module

    source_names = set(module.__dict__)
    assert not any(name.startswith("PySide") for name in source_names)
