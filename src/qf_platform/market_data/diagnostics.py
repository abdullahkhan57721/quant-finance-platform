"""Narrow static-arbitrage diagnostics for normalized option quote slices."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date

from qf_platform.market_data.normalization import NormalizedOptionObservation
from qf_platform.pricing.equity import OptionRight

_DIAGNOSTIC_RELATIVE_TOLERANCE = 1.0e-12


class IncomparableOptionSlice(ValueError):
    """Raised when observations do not form one comparable strike slice."""


@dataclass(frozen=True, slots=True)
class OptionSliceDiagnostics:
    """Monotonicity/convexity evidence for one same-right strike slice."""

    valuation_date: date
    expiry: date
    underlying_id: str
    right: OptionRight
    strikes: tuple[float, ...]
    monotonicity_violations: tuple[tuple[float, float], ...]
    convexity_violations: tuple[tuple[float, float, float], ...]

    @property
    def passes(self) -> bool:
        """Return whether the checked static strike conditions have no violations."""

        return not self.monotonicity_violations and not self.convexity_violations


def _comparison_tolerance(*values: float) -> float:
    return _DIAGNOSTIC_RELATIVE_TOLERANCE * max(1.0, *(abs(value) for value in values))


def diagnose_option_strike_slice(
    observations: Iterable[NormalizedOptionObservation],
    /,
) -> OptionSliceDiagnostics:
    """Diagnose monotonicity and convexity without repairing the observed slice.

    Observations must share valuation date, expiry, underlying identity, observed spot,
    and option right. Prices are the already-normalized target values. Duplicate strikes
    are rejected rather than silently aggregated.
    """

    ordered = sorted(observations, key=lambda observation: observation.raw_quote.strike)
    if len(ordered) < 2:
        msg = "strike diagnostics require at least two normalized observations"
        raise IncomparableOptionSlice(msg)

    first = ordered[0]
    valuation_date = first.valuation_date
    expiry = first.raw_quote.expiry
    underlying_id = first.raw_quote.underlying_id
    right = first.raw_quote.right
    spot = first.spot

    for observation in ordered[1:]:
        quote = observation.raw_quote
        if observation.valuation_date != valuation_date:
            msg = "strike diagnostics require one valuation date"
            raise IncomparableOptionSlice(msg)
        if quote.expiry != expiry:
            msg = "strike diagnostics require one expiry"
            raise IncomparableOptionSlice(msg)
        if quote.underlying_id != underlying_id:
            msg = "strike diagnostics require one underlying"
            raise IncomparableOptionSlice(msg)
        if quote.right is not right:
            msg = "strike diagnostics require one option right"
            raise IncomparableOptionSlice(msg)
        if observation.spot != spot:
            msg = "strike diagnostics require one observed underlying level"
            raise IncomparableOptionSlice(msg)

    strikes = tuple(observation.raw_quote.strike for observation in ordered)
    if len(set(strikes)) != len(strikes):
        msg = "strike diagnostics require unique strikes"
        raise IncomparableOptionSlice(msg)

    prices = tuple(observation.target_price for observation in ordered)
    monotonicity: list[tuple[float, float]] = []
    for index in range(len(ordered) - 1):
        left_price = prices[index]
        right_price = prices[index + 1]
        tolerance = _comparison_tolerance(left_price, right_price)
        if right is OptionRight.CALL:
            violated = right_price > left_price + tolerance
        else:
            violated = right_price < left_price - tolerance
        if violated:
            monotonicity.append((strikes[index], strikes[index + 1]))

    convexity: list[tuple[float, float, float]] = []
    for index in range(len(ordered) - 2):
        left_slope = (prices[index + 1] - prices[index]) / (
            strikes[index + 1] - strikes[index]
        )
        right_slope = (prices[index + 2] - prices[index + 1]) / (
            strikes[index + 2] - strikes[index + 1]
        )
        tolerance = _comparison_tolerance(left_slope, right_slope)
        if right_slope < left_slope - tolerance:
            convexity.append((strikes[index], strikes[index + 1], strikes[index + 2]))

    return OptionSliceDiagnostics(
        valuation_date=valuation_date,
        expiry=expiry,
        underlying_id=underlying_id,
        right=right,
        strikes=strikes,
        monotonicity_violations=tuple(monotonicity),
        convexity_violations=tuple(convexity),
    )
