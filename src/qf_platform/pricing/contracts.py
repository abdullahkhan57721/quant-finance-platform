"""Financial-contract semantics, separate from valuation algorithms."""

from __future__ import annotations

from typing import Protocol, TypeVar

from qf_platform.pricing.cashflows import CashFlowStream

PathT_contra = TypeVar("PathT_contra", contravariant=True)
TimeT = TypeVar("TimeT")


class FinancialContract(Protocol[PathT_contra, TimeT]):
    """Contingent cash-flow semantics for a modeled financial-state path."""

    def cash_flows(self, path: PathT_contra, /) -> CashFlowStream[TimeT]:
        """Return the realized contractual cash-flow stream for ``path``."""
