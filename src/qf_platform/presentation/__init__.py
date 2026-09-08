"""Renderer-neutral presentation values derived from authoritative quant semantics."""

from qf_platform.presentation.black_scholes import (
    BlackScholesPresentation,
    PayoffPoint,
    PresentationRow,
    build_black_scholes_presentation,
)

__all__ = [
    "BlackScholesPresentation",
    "PayoffPoint",
    "PresentationRow",
    "build_black_scholes_presentation",
]
