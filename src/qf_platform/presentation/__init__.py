"""Renderer-neutral presentation values derived from authoritative quant semantics."""

from qf_platform.presentation.black_scholes import (
    BlackScholesPresentation,
    PayoffPoint,
    PresentationRow,
    build_black_scholes_presentation,
)
from qf_platform.presentation.m2_workbench import (
    GreekComparisonRow,
    M2WorkbenchPresentation,
    ValuationComparisonRow,
    build_m2_workbench_presentation,
)
from qf_platform.presentation.plotting import PlotData, PlotPoint, PlotSeries
from qf_platform.presentation.ui3_hedging import (
    HedgeFrequencyRow,
    HedgeStepRow,
    HedgeWorkbenchPresentation,
    build_hedge_workbench_presentation,
    hedge_step_detail_rows,
)
from qf_platform.presentation.ui3_market import (
    MarketObservationDetail,
    MarketObservationRow,
    MarketWorkbenchPresentation,
    build_market_workbench_presentation,
)

__all__ = [
    "BlackScholesPresentation",
    "GreekComparisonRow",
    "HedgeFrequencyRow",
    "HedgeStepRow",
    "HedgeWorkbenchPresentation",
    "M2WorkbenchPresentation",
    "MarketObservationDetail",
    "MarketObservationRow",
    "MarketWorkbenchPresentation",
    "PayoffPoint",
    "PlotData",
    "PlotPoint",
    "PlotSeries",
    "PresentationRow",
    "ValuationComparisonRow",
    "build_black_scholes_presentation",
    "build_hedge_workbench_presentation",
    "build_m2_workbench_presentation",
    "build_market_workbench_presentation",
    "hedge_step_detail_rows",
]
