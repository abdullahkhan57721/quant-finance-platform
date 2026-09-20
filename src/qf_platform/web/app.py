"""Dash/Plotly sibling client for the quantitative research platform."""

# pyright: reportMissingTypeStubs=false, reportUnknownArgumentType=false, reportUnknownLambdaType=false, reportUnknownMemberType=false, reportUnknownParameterType=false, reportUnknownVariableType=false, reportUntypedFunctionDecorator=false

from __future__ import annotations

from collections.abc import Iterable, Sequence

from dash import Dash, Input, Output, State, dcc, html

from qf_platform.presentation import (
    HedgeWorkbenchPresentation,
    HestonCalibrationPresentation,
    HestonPricingPresentation,
    M2WorkbenchPresentation,
    M6MarketReferencePresentation,
    MarketWorkbenchPresentation,
    PlotData,
    PresentationRow,
    UI5PerformancePresentation,
    UI5ValidationPresentation,
)

from .plotly_adapter import figure_from_plot_data
from .services import (
    HedgingInputs,
    ServiceResult,
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

_PAGE_STYLE = {
    "fontFamily": "Inter, system-ui, sans-serif",
    "maxWidth": "1480px",
    "margin": "0 auto",
    "padding": "24px",
    "backgroundColor": "#f6f8fa",
    "minHeight": "100vh",
}
_PANEL_STYLE = {
    "backgroundColor": "white",
    "border": "1px solid #d0d7de",
    "borderRadius": "8px",
    "padding": "18px",
    "marginBottom": "16px",
}
_GRID_STYLE = {
    "display": "grid",
    "gridTemplateColumns": "repeat(auto-fit, minmax(180px, 1fr))",
    "gap": "12px",
    "marginBottom": "14px",
}
_INPUT_STYLE = {"width": "100%", "boxSizing": "border-box", "padding": "8px"}
_BUTTON_STYLE = {
    "padding": "9px 16px",
    "fontWeight": "600",
    "cursor": "pointer",
    "marginBottom": "12px",
}


def _input(label: str, component_id: str, value: str) -> html.Div:
    return html.Div(
        [
            html.Label(label, htmlFor=component_id, style={"fontWeight": "600"}),
            dcc.Input(
                id=component_id,
                value=value,
                type="text",
                debounce=True,
                style=_INPUT_STYLE,
            ),
        ]
    )


def _dropdown(
    label: str,
    component_id: str,
    value: str,
    options: Sequence[tuple[str, str]],
) -> html.Div:
    return html.Div(
        [
            html.Label(label, htmlFor=component_id, style={"fontWeight": "600"}),
            dcc.Dropdown(
                id=component_id,
                value=value,
                clearable=False,
                options=[{"label": text, "value": key} for text, key in options],
            ),
        ]
    )


def _section(title: str, children: Iterable[object]) -> html.Section:
    return html.Section(
        [html.H3(title, style={"marginTop": "0"}), *children],
        style=_PANEL_STYLE,
    )


def _simple_table(headers: Sequence[str], rows: Iterable[Sequence[object]]) -> html.Table:
    return html.Table(
        [
            html.Thead(html.Tr([html.Th(header) for header in headers])),
            html.Tbody(
                [
                    html.Tr([html.Td("" if value is None else str(value)) for value in row])
                    for row in rows
                ]
            ),
        ],
        style={"width": "100%", "borderCollapse": "collapse"},
    )


def _presentation_rows(rows: Sequence[PresentationRow]) -> html.Table:
    return _simple_table(
        ("Item", "Value", "Detail", "Status"),
        ((row.label, row.value, row.detail, row.status) for row in rows),
    )


def _graphs(*plots: PlotData) -> html.Div:
    return html.Div(
        [
            dcc.Graph(
                figure=figure_from_plot_data(plot),
                config={"displaylogo": False},
            )
            for plot in plots
        ],
        style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(420px, 1fr))"},
    )


def _error(message: str) -> html.Div:
    return html.Div(
        [html.Strong("Unable to run this study."), html.Div(message)],
        style={
            "backgroundColor": "#fff8c5",
            "border": "1px solid #d4a72c",
            "padding": "12px",
            "borderRadius": "6px",
        },
    )


def _prompt(text: str) -> html.Div:
    return html.Div(text, style={"color": "#57606a", "padding": "12px 0"})


def _render_service[T](
    result: ServiceResult[T],
    renderer,
) -> object:
    if result.error is not None:
        return _error(result.error)
    if result.value is None:
        return _error("service returned no value")
    return renderer(result.value)


def _render_valuation(presentation: M2WorkbenchPresentation) -> html.Div:
    return html.Div(
        [
            _section("Selected result", [_presentation_rows(presentation.result_rows)]),
            _section(
                "Valuation comparison",
                [
                    _simple_table(
                        ("Method", "Configuration", "PV", "Difference", "Evidence", "Status"),
                        (
                            (
                                row.method,
                                row.configuration,
                                row.present_value,
                                row.difference,
                                row.evidence,
                                row.status,
                            )
                            for row in presentation.valuation_rows
                        ),
                    )
                ],
            ),
            _section(
                "Greeks",
                [
                    _simple_table(
                        ("Greek", "Analytic", "Finite difference", "Difference", "Units", "Status"),
                        (
                            (
                                row.greek,
                                row.analytic,
                                row.finite_difference,
                                row.difference,
                                row.units,
                                row.status,
                            )
                            for row in presentation.greek_rows
                        ),
                    )
                ],
            ),
            _graphs(
                presentation.crr_plot,
                presentation.monte_carlo_plot,
                presentation.greek_plot,
            ),
        ]
    )


def _render_hedging(presentation: HedgeWorkbenchPresentation) -> html.Div:
    return html.Div(
        [
            _section("Selected replication path", [_presentation_rows(presentation.result_rows)]),
            _section("Aggregate evidence", [_presentation_rows(presentation.aggregate_rows)]),
            _section(
                "Rebalance cadence",
                [
                    _simple_table(
                        ("Cadence", "Replicates", "Mean error", "Std", "MAE", "RMSE"),
                        (
                            (
                                row.cadence,
                                row.replicates,
                                row.mean_error,
                                row.error_standard_deviation,
                                row.mean_absolute_error,
                                row.root_mean_square_error,
                            )
                            for row in presentation.frequency_rows
                        ),
                    )
                ],
            ),
            _graphs(presentation.frequency_plot, presentation.replicate_error_plot),
        ]
    )


def _render_market(presentation: MarketWorkbenchPresentation) -> html.Div:
    observation_rows = (
        (
            detail.table_row.contract_id,
            detail.table_row.expiry,
            detail.table_row.strike,
            detail.table_row.right,
            detail.table_row.normalized_price,
            detail.table_row.implied_volatility,
            detail.table_row.status,
        )
        for detail in presentation.observation_details
    )
    return html.Div(
        [
            _section("Derived empirical summary", [_presentation_rows(presentation.empirical_summary_rows)]),
            _section("Empirical provenance", [_presentation_rows(presentation.empirical_provenance_rows)]),
            _section(
                "Observation → normalization → inference",
                [
                    _simple_table(
                        ("Contract", "Expiry", "Strike", "Right", "Target", "Implied vol", "Status"),
                        observation_rows,
                    )
                ],
            ),
            _graphs(presentation.empirical_smile_plot, presentation.empirical_conditioning_plot),
        ]
    )


def _render_heston_pricing(presentation: HestonPricingPresentation) -> html.Div:
    return html.Div(
        [
            _section("Heston model", [_presentation_rows(presentation.parameter_rows)]),
            _section("Independent valuation evidence", [_presentation_rows(presentation.result_rows)]),
            _graphs(presentation.method_comparison_plot, presentation.fourier_stability_plot),
        ]
    )


def _render_heston_calibration(
    presentation: HestonCalibrationPresentation,
    market_reference: M6MarketReferencePresentation | None,
) -> html.Div:
    children: list[object] = [
        _section("Synthetic calibration question", [_presentation_rows(presentation.problem_rows)]),
        _section("Multiple starts and estimates", [_presentation_rows(presentation.run_rows)]),
        _section("Conditioning / identifiability", [_presentation_rows(presentation.conditioning_rows)]),
        _graphs(presentation.objective_plot, presentation.residual_plot),
    ]
    if market_reference is not None:
        children.extend(
            [
                _section("Recorded SPX calibration reference", [_presentation_rows(market_reference.summary_rows)]),
                _section("Recorded conditioning", [_presentation_rows(market_reference.conditioning_rows)]),
            ]
        )
    return html.Div(children)


def _render_validation(
    presentation: UI5ValidationPresentation,
    performance: UI5PerformancePresentation | None,
) -> html.Div:
    children: list[object] = [
        _section("Validation design", [_presentation_rows(presentation.summary_rows)]),
        _section("Held-out metrics", [_presentation_rows(presentation.evaluation_metric_rows)]),
        _section("Model-risk limits", [_presentation_rows(presentation.model_risk_rows)]),
        _section("Heston stability / conditioning", [_presentation_rows(presentation.stability_rows)]),
        _graphs(
            presentation.residual_plot,
            presentation.held_out_error_plot,
            presentation.parameter_stability_plot,
        ),
    ]
    if performance is not None:
        children.extend(
            [
                _section("Recorded M8 performance evidence", [_presentation_rows(performance.workload_rows)]),
                _section("Native-code decision", [_presentation_rows(performance.native_decision_rows)]),
                _graphs(performance.runtime_plot),
            ]
        )
    return html.Div(children)


def _overview_layout() -> html.Div:
    families = (
        ("Pricing & Greeks", "Forward valuation, numerical cross-validation, sensitivities"),
        ("Dynamic Hedging", "Replication error, cadence, misspecification, transaction costs"),
        ("Market / IV", "Observed quotes, normalization, inversion, skew and conditioning"),
        ("Heston", "Independent forward valuation, calibration, local identifiability"),
        ("Model Validation", "Predeclared train/held-out comparison and bounded conclusions"),
        ("Performance", "Revision-pinned M8 evidence and measured no-C++ decision"),
    )
    return html.Div(
        [
            html.H2("Quantitative Finance Research & Validation Platform"),
            html.P(
                "A validation-first internal analytics surface. Each workspace consumes the same "
                "typed application/evidence contracts used by Python, Jupyter, exports, and Qt."
            ),
            html.Div(
                [
                    html.Div(
                        [html.H3(title), html.P(detail)],
                        style=_PANEL_STYLE,
                    )
                    for title, detail in families
                ],
                style=_GRID_STYLE,
            ),
            _section(
                "Scientific boundary",
                [
                    html.P(
                        "The M7 result is a same-date cross-sectional holdout, not temporal "
                        "forecasting or historical trading profitability. M8 timings are recorded "
                        "revision-pinned evidence, not a benchmark of this browser session."
                    )
                ],
            ),
        ]
    )


def _valuation_layout() -> html.Div:
    defaults = ValuationInputs()
    return html.Div(
        [
            html.H2("Valuation & Greeks"),
            html.Div(
                [
                    _input("Spot", "val-spot", defaults.spot),
                    _input("Strike", "val-strike", defaults.strike),
                    _input("Valuation date", "val-date", defaults.valuation_date),
                    _input("Expiry", "val-expiry", defaults.expiry),
                    _input("Annualized volatility", "val-vol", defaults.annualized_volatility),
                    _input("Continuously compounded rate", "val-rate", defaults.continuously_compounded_rate),
                    _input("Continuous dividend yield", "val-q", defaults.continuous_dividend_yield),
                    _dropdown("Right", "val-right", defaults.option_right, (("Call", "call"), ("Put", "put"))),
                    _dropdown(
                        "Selected valuation",
                        "val-method",
                        defaults.valuation_method,
                        (("Analytic", "analytic"), ("CRR", "crr"), ("Monte Carlo", "monte_carlo")),
                    ),
                    _input("CRR steps", "val-crr", defaults.crr_steps),
                    _input("MC paths", "val-mc-paths", defaults.monte_carlo_paths),
                    _input("MC seed", "val-seed", defaults.monte_carlo_seed),
                    _dropdown(
                        "Greek",
                        "val-greek",
                        defaults.selected_greek,
                        (("Delta", "delta"), ("Gamma", "gamma"), ("Vega", "vega"), ("Theta", "theta"), ("Rho", "rho")),
                    ),
                ],
                style=_GRID_STYLE,
            ),
            html.Button("Run valuation study", id="val-run", n_clicks=0, style=_BUTTON_STYLE),
            dcc.Loading(html.Div(id="val-output", children=_prompt("Run the study to generate evidence."))),
        ]
    )


def _hedging_layout() -> html.Div:
    defaults = HedgingInputs()
    return html.Div(
        [
            html.H2("Dynamic Hedging"),
            html.P("Pricing-measure model-generated replication experiment; not a historical trading backtest."),
            html.Div(
                [
                    _input("Spot", "hedge-spot", defaults.spot),
                    _input("Strike", "hedge-strike", defaults.strike),
                    _input("Valuation date", "hedge-date", defaults.valuation_date),
                    _input("Expiry", "hedge-expiry", defaults.expiry),
                    _dropdown("Right", "hedge-right", defaults.option_right, (("Call", "call"), ("Put", "put"))),
                    _input("Generating volatility", "hedge-gen-vol", defaults.generating_volatility),
                    _input("Hedging volatility", "hedge-hedge-vol", defaults.hedging_volatility),
                    _input("Rebalance interval (days)", "hedge-days", defaults.rebalance_day_interval),
                    _input("Seed", "hedge-seed", defaults.seed),
                    _input("Replicates", "hedge-reps", defaults.replicate_count),
                    _input("Transaction cost rate", "hedge-cost", defaults.transaction_cost_rate),
                ],
                style=_GRID_STYLE,
            ),
            html.Button("Run hedge study", id="hedge-run", n_clicks=0, style=_BUTTON_STYLE),
            dcc.Loading(html.Div(id="hedge-output", children=_prompt("Run the study to generate replication evidence."))),
        ]
    )


def _market_layout() -> html.Div:
    return html.Div(
        [
            html.H2("Market / Implied Volatility"),
            html.P("Package-safe M4 evidence; default operation performs no network retrieval."),
            html.Button("Load market evidence", id="market-run", n_clicks=0, style=_BUTTON_STYLE),
            dcc.Loading(html.Div(id="market-output", children=_prompt("Load the package-safe M4 evidence."))),
        ]
    )


def _heston_layout() -> html.Div:
    return html.Div(
        [
            html.H2("Heston Pricing & Calibration"),
            _section(
                "Forward valuation",
                [
                    html.P("Run the default typed M5 problem through independent Fourier and Monte Carlo methods."),
                    html.Button("Run Heston pricing", id="heston-price-run", n_clicks=0, style=_BUTTON_STYLE),
                    dcc.Loading(html.Div(id="heston-price-output", children=_prompt("Run the pricing study."))),
                ],
            ),
            _section(
                "Calibration / identifiability",
                [
                    _dropdown(
                        "Synthetic calibration study",
                        "heston-cal-mode",
                        "recovery",
                        (("Truth recovery", "recovery"), ("Thin non-identifiability", "thin")),
                    ),
                    html.Button("Run Heston calibration", id="heston-cal-run", n_clicks=0, style=_BUTTON_STYLE),
                    dcc.Loading(html.Div(id="heston-cal-output", children=_prompt("Run the calibration study."))),
                ],
            ),
        ]
    )


def _validation_layout() -> html.Div:
    return html.Div(
        [
            html.H2("Model Validation"),
            html.P(
                "Predeclared same-date cross-sectional M7 holdout plus revision-pinned M8 performance evidence."
            ),
            html.Button("Run validation study", id="validation-run", n_clicks=0, style=_BUTTON_STYLE),
            dcc.Loading(html.Div(id="validation-output", children=_prompt("Run the reference validation study."))),
        ]
    )


def create_dash_app() -> Dash:
    """Construct the local analytics application without executing expensive studies."""

    app = Dash(__name__, title="Quant Finance Analytics Workbench")
    app.layout = html.Div(
        [
            dcc.Tabs(
                id="workspace-tabs",
                value="overview",
                children=[
                    dcc.Tab(label="Overview", value="overview", children=[_overview_layout()]),
                    dcc.Tab(label="Valuation & Greeks", value="valuation", children=[_valuation_layout()]),
                    dcc.Tab(label="Dynamic Hedging", value="hedging", children=[_hedging_layout()]),
                    dcc.Tab(label="Market / IV", value="market", children=[_market_layout()]),
                    dcc.Tab(label="Heston", value="heston", children=[_heston_layout()]),
                    dcc.Tab(label="Model Validation", value="validation", children=[_validation_layout()]),
                ],
            )
        ],
        style=_PAGE_STYLE,
    )

    @app.callback(
        Output("val-output", "children"),
        Input("val-run", "n_clicks"),
        State("val-spot", "value"),
        State("val-strike", "value"),
        State("val-date", "value"),
        State("val-expiry", "value"),
        State("val-vol", "value"),
        State("val-rate", "value"),
        State("val-q", "value"),
        State("val-right", "value"),
        State("val-method", "value"),
        State("val-crr", "value"),
        State("val-mc-paths", "value"),
        State("val-seed", "value"),
        State("val-greek", "value"),
    )
    def run_valuation_callback(n_clicks, *values):
        if not n_clicks:
            return _prompt("Run the study to generate evidence.")
        inputs = ValuationInputs(*("" if value is None else str(value) for value in values))
        return _render_service(run_valuation_service(inputs), _render_valuation)

    @app.callback(
        Output("hedge-output", "children"),
        Input("hedge-run", "n_clicks"),
        State("hedge-spot", "value"),
        State("hedge-strike", "value"),
        State("hedge-date", "value"),
        State("hedge-expiry", "value"),
        State("hedge-right", "value"),
        State("hedge-gen-vol", "value"),
        State("hedge-hedge-vol", "value"),
        State("hedge-days", "value"),
        State("hedge-seed", "value"),
        State("hedge-reps", "value"),
        State("hedge-cost", "value"),
    )
    def run_hedging_callback(n_clicks, *values):
        if not n_clicks:
            return _prompt("Run the study to generate replication evidence.")
        inputs = HedgingInputs(*("" if value is None else str(value) for value in values))
        return _render_service(run_hedging_service(inputs), _render_hedging)

    @app.callback(Output("market-output", "children"), Input("market-run", "n_clicks"))
    def run_market_callback(n_clicks):
        if not n_clicks:
            return _prompt("Load the package-safe M4 evidence.")
        return _render_service(load_market_service(), _render_market)

    @app.callback(
        Output("heston-price-output", "children"),
        Input("heston-price-run", "n_clicks"),
    )
    def run_heston_pricing_callback(n_clicks):
        if not n_clicks:
            return _prompt("Run the pricing study.")
        return _render_service(run_heston_pricing_service(), _render_heston_pricing)

    @app.callback(
        Output("heston-cal-output", "children"),
        Input("heston-cal-run", "n_clicks"),
        State("heston-cal-mode", "value"),
    )
    def run_heston_calibration_callback(n_clicks, mode):
        if not n_clicks:
            return _prompt("Run the calibration study.")
        calibration = run_heston_calibration_service(str(mode or "recovery"))
        if calibration.error is not None:
            return _error(calibration.error)
        reference_result = load_m6_market_reference_service()
        reference = reference_result.value if reference_result.error is None else None
        if calibration.value is None:
            return _error("calibration service returned no value")
        return _render_heston_calibration(calibration.value, reference)

    @app.callback(
        Output("validation-output", "children"),
        Input("validation-run", "n_clicks"),
    )
    def run_validation_callback(n_clicks):
        if not n_clicks:
            return _prompt("Run the reference validation study.")
        validation = load_validation_service()
        if validation.error is not None:
            return _error(validation.error)
        performance_result = load_performance_service()
        performance = performance_result.value if performance_result.error is None else None
        if validation.value is None:
            return _error("validation service returned no value")
        return _render_validation(validation.value, performance)

    return app
