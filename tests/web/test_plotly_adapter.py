"""Plotly terminal-renderer tests over renderer-neutral PlotData."""

from __future__ import annotations

from qf_platform.presentation import PlotData, PlotPoint, PlotSeries
from qf_platform.web.plotly_adapter import figure_from_plot_data


def test_plotly_adapter_preserves_points_and_uncertainty() -> None:
    plot = PlotData(
        title="Evidence",
        x_label="x",
        y_label="y",
        series=(
            PlotSeries(
                key="sample",
                label="Sample",
                points=(
                    PlotPoint(1.0, 2.0, lower=1.5, upper=2.7),
                    PlotPoint(2.0, 3.0),
                ),
            ),
        ),
    )

    payload = figure_from_plot_data(plot).to_plotly_json()
    trace = payload["data"][0]
    assert list(trace["x"]) == [1.0, 2.0]
    assert list(trace["y"]) == [2.0, 3.0]
    assert list(trace["error_y"]["array"]) == [0.7, 0.0]
    assert list(trace["error_y"]["arrayminus"]) == [0.5, 0.0]
    assert payload["layout"]["title"]["text"] == "Evidence"
