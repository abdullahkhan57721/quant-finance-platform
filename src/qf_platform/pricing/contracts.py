"""Financial-contract semantics, separate from valuation algorithms."""

from __future__ import annotations

from typing import Protocol

from qf_platform.pricing.cashflows import CashFlowStream
from qf_platform.pricing.state import StatePath


class FinancialContract[TimeT, StateT](Protocol):
    """Contingent cash-flow semantics for a modeled financial-state path."""

    def cash_flows(
        self,
        path: StatePath[TimeT, StateT],
        /,
    ) -> CashFlowStream[TimeT]:
        """Return the realized contractual cash-flow stream for ``path``."""
        ...
