"""Explicit option-quote normalization for the first M4 inverse consumer."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from typing import cast

from qf_platform._validation import finite_real
from qf_platform.market_data.observations import (
    OptionExerciseStyle,
    OptionSettlementTime,
    RawOptionQuote,
    RawUnderlyingObservation,
)

_NORMALIZATION_VERSION = "m4-midpoint-v1"


class QuoteSelection(StrEnum):
    """Observed-price derivation used by a normalized option observation."""

    MIDPOINT = "midpoint"


class QuoteNormalizationError(ValueError):
    """Raised when raw observations cannot become problem-ready market information."""


@dataclass(frozen=True, slots=True)
class NormalizedOptionObservation:
    """Problem-ready market information retaining its raw observation lineage."""

    raw_quote: RawOptionQuote
    raw_underlying: RawUnderlyingObservation
    target_price: float
    spot: float
    quote_selection: QuoteSelection = QuoteSelection.MIDPOINT
    normalization_version: str = _NORMALIZATION_VERSION

    def __post_init__(self) -> None:
        if not isinstance(cast(object, self.raw_quote), RawOptionQuote):
            msg = "raw_quote must be a RawOptionQuote"
            raise TypeError(msg)
        if not isinstance(cast(object, self.raw_underlying), RawUnderlyingObservation):
            msg = "raw_underlying must be a RawUnderlyingObservation"
            raise TypeError(msg)
        target_price = finite_real(self.target_price, name="target_price")
        spot = finite_real(self.spot, name="spot")
        if target_price <= 0.0:
            msg = "target_price must be positive"
            raise ValueError(msg)
        if spot <= 0.0:
            msg = "spot must be positive"
            raise ValueError(msg)
        object.__setattr__(self, "target_price", target_price)
        object.__setattr__(self, "spot", spot)
        if not isinstance(cast(object, self.quote_selection), QuoteSelection):
            msg = "quote_selection must be a QuoteSelection"
            raise TypeError(msg)
        if not self.normalization_version.strip():
            msg = "normalization_version must be non-empty"
            raise ValueError(msg)

    @property
    def valuation_date(self) -> date:
        """Return the source market date used as M1's date-valued valuation time."""

        return self.raw_quote.provenance.market_date


def normalize_european_option_midpoint(
    quote: RawOptionQuote,
    underlying: RawUnderlyingObservation,
    /,
) -> NormalizedOptionObservation:
    """Normalize one European PM-settled option with a positive midpoint policy.

    The first M4 policy deliberately does not infer stale-quote status when the source
    lacks contract-level timestamps. It requires explicit PM settlement because M1's
    date-only expiry semantics cannot faithfully represent AM or unknown settlement
    timing.
    """

    if quote.underlying_id != underlying.underlying_id:
        msg = "option and underlying observations must reference the same underlying"
        raise QuoteNormalizationError(msg)
    if quote.provenance.market_date != underlying.provenance.market_date:
        msg = "option and underlying observations must share one market date"
        raise QuoteNormalizationError(msg)
    if quote.exercise_style is not OptionExerciseStyle.EUROPEAN:
        msg = "M4 midpoint normalization supports European exercise only"
        raise QuoteNormalizationError(msg)
    if quote.settlement_time is not OptionSettlementTime.PM:
        msg = "M4 midpoint normalization requires explicit PM settlement semantics"
        raise QuoteNormalizationError(msg)

    bid = quote.bid
    ask = quote.ask
    if bid is None or ask is None:
        msg = "midpoint normalization requires both bid and ask"
        raise QuoteNormalizationError(msg)
    if bid <= 0.0 or ask <= 0.0:
        msg = "midpoint normalization requires positive bid and ask"
        raise QuoteNormalizationError(msg)
    if bid > ask:
        msg = "crossed option quote cannot be normalized"
        raise QuoteNormalizationError(msg)
    if underlying.value <= 0.0:
        msg = "problem-ready underlying level must be positive"
        raise QuoteNormalizationError(msg)

    return NormalizedOptionObservation(
        raw_quote=quote,
        raw_underlying=underlying,
        target_price=0.5 * (bid + ask),
        spot=underlying.value,
    )
