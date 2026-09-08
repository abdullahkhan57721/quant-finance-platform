"""Immutable contingent cash-flow value semantics."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True, slots=True)
class CashFlow[TimeT]:
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
class CashFlowStream[TimeT]:
    """An immutable ordered collection of realized cash flows."""

    cash_flows: tuple[CashFlow[TimeT], ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "cash_flows", tuple(self.cash_flows))

    def __iter__(self) -> Iterator[CashFlow[TimeT]]:
        return iter(self.cash_flows)

    def __len__(self) -> int:
        return len(self.cash_flows)
