"""Immutable contingent cash-flow value semantics."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Generic, Iterator, TypeVar

TimeT = TypeVar("TimeT")


@dataclass(frozen=True, slots=True)
class CashFlow(Generic[TimeT]):
    """One finite payment amount at a payment time."""

    payment_time: TimeT
    amount: float

    def __post_init__(self) -> None:
        amount = float(self.amount)
        if not isfinite(amount):
            msg = "cash-flow amount must be finite"
            raise ValueError(msg)
        object.__setattr__(self, "amount", amount)


@dataclass(frozen=True, slots=True)
class CashFlowStream(Generic[TimeT]):
    """An immutable ordered collection of realized cash flows."""

    cash_flows: tuple[CashFlow[TimeT], ...]

    def __iter__(self) -> Iterator[CashFlow[TimeT]]:
        return iter(self.cash_flows)

    def __len__(self) -> int:
        return len(self.cash_flows)
