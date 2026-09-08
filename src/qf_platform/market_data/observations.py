"""Immutable raw market observations and source provenance for M4."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum
from math import isfinite
from typing import cast

from qf_platform._validation import calendar_date, finite_real
from qf_platform.pricing.equity import OptionRight


def _nonempty_text(value: object, *, name: str) -> str:
    if not isinstance(value, str):
        msg = f"{name} must be a string"
        raise TypeError(msg)
    normalized = value.strip()
    if not normalized:
        msg = f"{name} must be non-empty"
        raise ValueError(msg)
    return normalized


def _aware_datetime(value: object, *, name: str) -> datetime:
    if not isinstance(value, datetime):
        msg = f"{name} must be a datetime"
        raise TypeError(msg)
    if value.tzinfo is None or value.utcoffset() is None:
        msg = f"{name} must be timezone-aware"
        raise ValueError(msg)
    return value


def _optional_aware_datetime(value: object, *, name: str) -> datetime | None:
    if value is None:
        return None
    return _aware_datetime(value, name=name)


def _optional_finite_real(value: object, *, name: str) -> float | None:
    if value is None:
        return None
    return finite_real(value, name=name)


def _optional_count(value: object, *, name: str) -> int | None:
    if value is None:
        return None
    if type(value) is not int:
        msg = f"{name} must be an integer"
        raise TypeError(msg)
    if value < 0:
        msg = f"{name} must be non-negative"
        raise ValueError(msg)
    return value


def _optional_sha256(value: object) -> str | None:
    if value is None:
        return None
    normalized = _nonempty_text(value, name="raw_artifact_sha256").lower()
    if len(normalized) != 64 or any(
        character not in "0123456789abcdef" for character in normalized
    ):
        msg = "raw_artifact_sha256 must contain exactly 64 hexadecimal characters"
        raise ValueError(msg)
    return normalized


class OptionExerciseStyle(StrEnum):
    """Exercise style reported by the market-data source."""

    EUROPEAN = "european"
    AMERICAN = "american"


class OptionSettlementTime(StrEnum):
    """Coarse settlement-time convention when the source reports one."""

    AM = "am"
    PM = "pm"


@dataclass(frozen=True, slots=True)
class ObservationProvenance:
    """Source identity and timing for one immutable raw observation.

    ``market_date`` is always required because the M1 pricing vertical is date-based.
    ``observed_at`` is optional because historical end-of-day sources may not preserve
    contract-level quote timestamps. When present, timestamps must be timezone-aware.
    """

    provider: str
    source: str
    market_date: date
    retrieved_at: datetime
    observed_at: datetime | None = None
    raw_artifact_sha256: str | None = None
    license_notes: str = "unspecified"

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "provider", _nonempty_text(self.provider, name="provider")
        )
        object.__setattr__(self, "source", _nonempty_text(self.source, name="source"))
        object.__setattr__(
            self,
            "market_date",
            calendar_date(self.market_date, name="market_date"),
        )
        retrieved_at = _aware_datetime(self.retrieved_at, name="retrieved_at")
        observed_at = _optional_aware_datetime(self.observed_at, name="observed_at")
        if observed_at is not None and observed_at > retrieved_at:
            msg = "observed_at cannot be later than retrieved_at"
            raise ValueError(msg)
        object.__setattr__(self, "retrieved_at", retrieved_at)
        object.__setattr__(self, "observed_at", observed_at)
        object.__setattr__(
            self,
            "raw_artifact_sha256",
            _optional_sha256(self.raw_artifact_sha256),
        )
        object.__setattr__(
            self,
            "license_notes",
            _nonempty_text(self.license_notes, name="license_notes"),
        )


@dataclass(frozen=True, slots=True)
class RawOptionQuote:
    """Raw option quote evidence before quote-quality normalization.

    Quote prices deliberately admit finite negative or crossed values here. Those are
    observations of bad data, not constructor errors; normalization decides whether a
    quote can become problem-ready information.
    """

    contract_id: str
    underlying_id: str
    expiry: date
    strike: float
    right: OptionRight
    exercise_style: OptionExerciseStyle
    provenance: ObservationProvenance
    bid: float | None = None
    ask: float | None = None
    last: float | None = None
    volume: int | None = None
    open_interest: int | None = None
    settlement_time: OptionSettlementTime | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "contract_id", _nonempty_text(self.contract_id, name="contract_id")
        )
        object.__setattr__(
            self,
            "underlying_id",
            _nonempty_text(self.underlying_id, name="underlying_id"),
        )
        object.__setattr__(self, "expiry", calendar_date(self.expiry, name="expiry"))
        strike = finite_real(self.strike, name="strike")
        if strike < 0.0:
            msg = "strike must be non-negative"
            raise ValueError(msg)
        object.__setattr__(self, "strike", strike)
        if not isinstance(cast(object, self.right), OptionRight):
            msg = "right must be an OptionRight"
            raise TypeError(msg)
        if not isinstance(cast(object, self.exercise_style), OptionExerciseStyle):
            msg = "exercise_style must be an OptionExerciseStyle"
            raise TypeError(msg)
        if not isinstance(cast(object, self.provenance), ObservationProvenance):
            msg = "provenance must be ObservationProvenance"
            raise TypeError(msg)
        for name in ("bid", "ask", "last"):
            object.__setattr__(
                self,
                name,
                _optional_finite_real(getattr(self, name), name=name),
            )
        object.__setattr__(self, "volume", _optional_count(self.volume, name="volume"))
        object.__setattr__(
            self,
            "open_interest",
            _optional_count(self.open_interest, name="open_interest"),
        )
        settlement = self.settlement_time
        if settlement is not None and not isinstance(
            cast(object, settlement), OptionSettlementTime
        ):
            msg = "settlement_time must be an OptionSettlementTime or None"
            raise TypeError(msg)


@dataclass(frozen=True, slots=True)
class RawUnderlyingObservation:
    """Raw observed underlying level, distinct from modeled ``EquityState``."""

    underlying_id: str
    value: float
    provenance: ObservationProvenance

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "underlying_id",
            _nonempty_text(self.underlying_id, name="underlying_id"),
        )
        value = finite_real(self.value, name="underlying value")
        if not isfinite(value):
            msg = "underlying value must be finite"
            raise ValueError(msg)
        object.__setattr__(self, "value", value)
        if not isinstance(cast(object, self.provenance), ObservationProvenance):
            msg = "provenance must be ObservationProvenance"
            raise TypeError(msg)
