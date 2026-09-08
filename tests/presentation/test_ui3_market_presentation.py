from __future__ import annotations

from qf_platform.application.ui3_market import canonical_m4_market_workbench
from qf_platform.presentation.ui3_market import build_market_workbench_presentation


def test_market_presentation_preserves_observation_inverse_and_empirical_layers() -> (
    None
):
    presentation = build_market_workbench_presentation(canonical_m4_market_workbench())

    assert len(presentation.observation_details) == 10
    first = presentation.observation_details[0]
    assert first.table_row.status == "Normalized + inferred"
    assert {row.label for row in first.provenance_rows} >= {
        "Raw contract id",
        "Provider",
        "Market date",
        "Raw artifact SHA-256",
        "Normalization",
    }
    assert {row.label for row in first.inverse_rows} >= {
        "Observed target",
        "Implied volatility",
        "Vega at solution",
        "dVol / dPrice",
        "Half-spread IV shift",
    }
    assert {row.label for row in first.inspector_rows} == {
        "Observed target",
        "Forward model",
        "Unknown parameter",
        "Admissible domain",
        "Inverse method",
        "Conditioning evidence",
    }
    assert len(presentation.synthetic_smile_plot.series) == 2
    assert len(presentation.empirical_smile_plot.series) == 2
    assert any(
        "raw rows are not redistributed" in row.value
        for row in presentation.empirical_provenance_rows
    )
    assert all(
        "no repair" in row.status.lower() for row in presentation.diagnostic_rows
    )
