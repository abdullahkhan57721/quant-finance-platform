"""Dash application construction and headless route smoke tests."""

# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false

from __future__ import annotations

from collections.abc import Iterator
from typing import Any, cast

from qf_platform.web import create_dash_app


def _walk(component: Any) -> Iterator[Any]:
    yield component
    children = getattr(component, "children", None)
    if isinstance(children, (list, tuple)):
        for child in children:
            yield from _walk(child)
    elif children is not None and not isinstance(children, (str, int, float, bool)):
        yield from _walk(children)


def test_dash_app_contains_all_f4_workspaces_and_callbacks() -> None:
    app = create_dash_app()
    assert app.layout is not None

    components = tuple(_walk(app.layout))
    labels = {
        component.label
        for component in components
        if component.__class__.__name__ == "Tab"
    }
    assert labels == {
        "Overview",
        "Valuation & Greeks",
        "Dynamic Hedging",
        "Market / IV",
        "Heston",
        "Model Validation",
    }

    ids = {
        component_id
        for component in components
        if (component_id := getattr(component, "id", None)) is not None
    }
    assert {
        "workspace-tabs",
        "val-run",
        "hedge-run",
        "market-run",
        "heston-price-run",
        "heston-cal-run",
        "validation-run",
    } <= ids
    callback_map = cast(dict[object, object], app.callback_map)
    assert len(callback_map) == 6


def test_dash_server_and_layout_endpoints_smoke() -> None:
    app = create_dash_app()
    client = app.server.test_client()

    root = client.get("/")
    assert root.status_code == 200
    assert b"Quant Finance Analytics Workbench" in root.data

    layout = client.get("/_dash-layout")
    assert layout.status_code == 200
    assert b"workspace-tabs" in layout.data
