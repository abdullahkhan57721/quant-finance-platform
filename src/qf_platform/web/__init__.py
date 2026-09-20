"""Dash/Plotly browser client over frontend-neutral quantitative semantics."""

from .app import create_dash_app
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

__all__ = [
    "HedgingInputs",
    "ServiceResult",
    "ValuationInputs",
    "create_dash_app",
    "figure_from_plot_data",
    "load_m6_market_reference_service",
    "load_market_service",
    "load_performance_service",
    "load_validation_service",
    "run_hedging_service",
    "run_heston_calibration_service",
    "run_heston_pricing_service",
    "run_valuation_service",
]
