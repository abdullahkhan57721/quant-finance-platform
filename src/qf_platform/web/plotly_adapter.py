"""Terminal Plotly renderer for renderer-neutral presentation PlotData."""

# pyright: reportArgumentType=false, reportMissingTypeStubs=false, reportUnknownArgumentType=false, reportUnknownMemberType=false, reportUnknownVariableType=false

from __future__ import annotations

import plotly.graph_objects as go

from qf_platform.presentation import PlotData


def figure_from_plot_data(plot: PlotData) -> go.Figure:
    """Render existing PlotData without introducing quantitative semantics."""

    figure = go.Figure()
    for series in plot.series:
        x = [point.x for point in series.points]
        y = [point.y for point in series.points]
        has_uncertainty = any(
            point.lower is not None and point.upper is not None
            for point in series.points
        )
        error_y = None
        if has_uncertainty:
            upper = [
                0.0 if point.upper is None else point.upper - point.y
                for point in series.points
            ]
            lower = [
                0.0 if point.lower is None else point.y - point.lower
                for point in series.points
            ]
            error_y = {
                "type": "data",
                "symmetric": False,
                "array": upper,
                "arrayminus": lower,
                "visible": True,
            }
        figure.add_trace(
            go.Scatter(
                x=x,
                y=y,
                name=series.label,
                mode="lines+markers",
                error_y=error_y,
            )
        )
    figure.update_layout(
        title=plot.title,
        xaxis_title=plot.x_label,
        yaxis_title=plot.y_label,
        template="plotly_white",
        margin={"l": 50, "r": 25, "t": 55, "b": 45},
        legend={"orientation": "h"},
    )
    return figure
