"""Minimal renderer-neutral plotting values shared by concrete Workbench views."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True, slots=True)
class PlotPoint:
    """One numeric point with optional vertical uncertainty bounds."""

    x: float
    y: float
    lower: float | None = None
    upper: float | None = None

    def __post_init__(self) -> None:
        x = float(self.x)
        y = float(self.y)
        if not isfinite(x) or not isfinite(y):
            raise ValueError("plot coordinates must be finite")
        object.__setattr__(self, "x", x)
        object.__setattr__(self, "y", y)
        if self.lower is None and self.upper is None:
            return
        if self.lower is None or self.upper is None:
            raise ValueError("plot uncertainty requires both lower and upper bounds")
        lower = float(self.lower)
        upper = float(self.upper)
        if not isfinite(lower) or not isfinite(upper):
            raise ValueError("plot uncertainty bounds must be finite")
        if lower > upper:
            raise ValueError("plot lower bound must not exceed upper bound")
        object.__setattr__(self, "lower", lower)
        object.__setattr__(self, "upper", upper)


@dataclass(frozen=True, slots=True)
class PlotSeries:
    """One labeled renderer-neutral series; styling remains renderer-owned."""

    key: str
    label: str
    points: tuple[PlotPoint, ...]


@dataclass(frozen=True, slots=True)
class PlotData:
    """Small shared plot payload earned by payoff, convergence, and Greek views."""

    title: str
    x_label: str
    y_label: str
    series: tuple[PlotSeries, ...]
