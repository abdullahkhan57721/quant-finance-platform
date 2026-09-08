"""Curated Qt models for renderer-neutral presentation values."""

from __future__ import annotations

from PySide6.QtCore import (
    QAbstractListModel,
    QByteArray,
    QModelIndex,
    QPersistentModelIndex,
    Qt,
)

from qf_platform.presentation import (
    GreekComparisonRow,
    HedgeFrequencyRow,
    HedgeStepRow,
    MarketObservationRow,
    PresentationRow,
    ValuationComparisonRow,
)

_INVALID_INDEX: QModelIndex | QPersistentModelIndex = QModelIndex()
_LABEL_ROLE = int(Qt.ItemDataRole.UserRole) + 1
_VALUE_ROLE = _LABEL_ROLE + 1
_DETAIL_ROLE = _LABEL_ROLE + 2
_STATUS_ROLE = _LABEL_ROLE + 3


class PresentationRowModel(QAbstractListModel):
    """Expose presentation rows without exposing finance-domain object graphs."""

    def __init__(self) -> None:
        super().__init__()
        self._items: tuple[PresentationRow, ...] = ()

    def rowCount(  # noqa: N802
        self,
        parent: QModelIndex | QPersistentModelIndex = _INVALID_INDEX,
    ) -> int:
        if parent.isValid():
            return 0
        return len(self._items)

    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        role: int = int(Qt.ItemDataRole.DisplayRole),
    ) -> object | None:
        if not index.isValid() or not 0 <= index.row() < len(self._items):
            return None
        item = self._items[index.row()]
        return {
            _LABEL_ROLE: item.label,
            _VALUE_ROLE: item.value,
            _DETAIL_ROLE: item.detail,
            _STATUS_ROLE: item.status,
        }.get(role)

    def roleNames(self) -> dict[int, QByteArray]:  # noqa: N802
        return {
            _LABEL_ROLE: QByteArray(b"label"),
            _VALUE_ROLE: QByteArray(b"value"),
            _DETAIL_ROLE: QByteArray(b"detail"),
            _STATUS_ROLE: QByteArray(b"status"),
        }

    def set_items(self, items: tuple[PresentationRow, ...]) -> None:
        """Replace rows atomically after Python semantics prepare them."""
        self.beginResetModel()
        self._items = items
        self.endResetModel()


_METHOD_ROLE = int(Qt.ItemDataRole.UserRole) + 1
_CONFIGURATION_ROLE = _METHOD_ROLE + 1
_PRESENT_VALUE_ROLE = _METHOD_ROLE + 2
_DIFFERENCE_ROLE = _METHOD_ROLE + 3
_EVIDENCE_ROLE = _METHOD_ROLE + 4
_TABLE_STATUS_ROLE = _METHOD_ROLE + 5


class ValuationComparisonModel(QAbstractListModel):
    """Expose the concrete UI2 method-comparison table."""

    def __init__(self) -> None:
        super().__init__()
        self._items: tuple[ValuationComparisonRow, ...] = ()

    def rowCount(  # noqa: N802
        self,
        parent: QModelIndex | QPersistentModelIndex = _INVALID_INDEX,
    ) -> int:
        if parent.isValid():
            return 0
        return len(self._items)

    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        role: int = int(Qt.ItemDataRole.DisplayRole),
    ) -> object | None:
        if not index.isValid() or not 0 <= index.row() < len(self._items):
            return None
        item = self._items[index.row()]
        return {
            _METHOD_ROLE: item.method,
            _CONFIGURATION_ROLE: item.configuration,
            _PRESENT_VALUE_ROLE: item.present_value,
            _DIFFERENCE_ROLE: item.difference,
            _EVIDENCE_ROLE: item.evidence,
            _TABLE_STATUS_ROLE: item.status,
        }.get(role)

    def roleNames(self) -> dict[int, QByteArray]:  # noqa: N802
        return {
            _METHOD_ROLE: QByteArray(b"method"),
            _CONFIGURATION_ROLE: QByteArray(b"configuration"),
            _PRESENT_VALUE_ROLE: QByteArray(b"presentValue"),
            _DIFFERENCE_ROLE: QByteArray(b"difference"),
            _EVIDENCE_ROLE: QByteArray(b"evidence"),
            _TABLE_STATUS_ROLE: QByteArray(b"status"),
        }

    def set_items(self, items: tuple[ValuationComparisonRow, ...]) -> None:
        self.beginResetModel()
        self._items = items
        self.endResetModel()


_GREEK_ROLE = int(Qt.ItemDataRole.UserRole) + 1
_ANALYTIC_ROLE = _GREEK_ROLE + 1
_FINITE_DIFFERENCE_ROLE = _GREEK_ROLE + 2
_GREEK_DIFFERENCE_ROLE = _GREEK_ROLE + 3
_UNITS_ROLE = _GREEK_ROLE + 4
_GREEK_STATUS_ROLE = _GREEK_ROLE + 5


class GreekComparisonModel(QAbstractListModel):
    """Expose the concrete M2 analytic-versus-finite-difference table."""

    def __init__(self) -> None:
        super().__init__()
        self._items: tuple[GreekComparisonRow, ...] = ()

    def rowCount(  # noqa: N802
        self,
        parent: QModelIndex | QPersistentModelIndex = _INVALID_INDEX,
    ) -> int:
        if parent.isValid():
            return 0
        return len(self._items)

    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        role: int = int(Qt.ItemDataRole.DisplayRole),
    ) -> object | None:
        if not index.isValid() or not 0 <= index.row() < len(self._items):
            return None
        item = self._items[index.row()]
        return {
            _GREEK_ROLE: item.greek,
            _ANALYTIC_ROLE: item.analytic,
            _FINITE_DIFFERENCE_ROLE: item.finite_difference,
            _GREEK_DIFFERENCE_ROLE: item.difference,
            _UNITS_ROLE: item.units,
            _GREEK_STATUS_ROLE: item.status,
        }.get(role)

    def roleNames(self) -> dict[int, QByteArray]:  # noqa: N802
        return {
            _GREEK_ROLE: QByteArray(b"greek"),
            _ANALYTIC_ROLE: QByteArray(b"analytic"),
            _FINITE_DIFFERENCE_ROLE: QByteArray(b"finiteDifference"),
            _GREEK_DIFFERENCE_ROLE: QByteArray(b"difference"),
            _UNITS_ROLE: QByteArray(b"units"),
            _GREEK_STATUS_ROLE: QByteArray(b"status"),
        }

    def set_items(self, items: tuple[GreekComparisonRow, ...]) -> None:
        self.beginResetModel()
        self._items = items
        self.endResetModel()


_HEDGE_TIME_ROLE = int(Qt.ItemDataRole.UserRole) + 1
_HEDGE_SPOT_ROLE = _HEDGE_TIME_ROLE + 1
_HEDGE_OPTION_VALUE_ROLE = _HEDGE_TIME_ROLE + 2
_HEDGE_STOCK_UNITS_ROLE = _HEDGE_TIME_ROLE + 3
_HEDGE_TRADE_UNITS_ROLE = _HEDGE_TIME_ROLE + 4
_HEDGE_CASH_ROLE = _HEDGE_TIME_ROLE + 5
_HEDGE_VALUE_ROLE = _HEDGE_TIME_ROLE + 6
_HEDGE_COST_ROLE = _HEDGE_TIME_ROLE + 7


class HedgeStepModel(QAbstractListModel):
    """Expose authoritative M3 rebalance rows to QML."""

    def __init__(self) -> None:
        super().__init__()
        self._items: tuple[HedgeStepRow, ...] = ()

    def rowCount(  # noqa: N802
        self,
        parent: QModelIndex | QPersistentModelIndex = _INVALID_INDEX,
    ) -> int:
        return 0 if parent.isValid() else len(self._items)

    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        role: int = int(Qt.ItemDataRole.DisplayRole),
    ) -> object | None:
        if not index.isValid() or not 0 <= index.row() < len(self._items):
            return None
        item = self._items[index.row()]
        return {
            _HEDGE_TIME_ROLE: item.time,
            _HEDGE_SPOT_ROLE: item.spot,
            _HEDGE_OPTION_VALUE_ROLE: item.option_value,
            _HEDGE_STOCK_UNITS_ROLE: item.stock_units,
            _HEDGE_TRADE_UNITS_ROLE: item.trade_units,
            _HEDGE_CASH_ROLE: item.cash_account,
            _HEDGE_VALUE_ROLE: item.hedge_value,
            _HEDGE_COST_ROLE: item.transaction_cost,
        }.get(role)

    def roleNames(self) -> dict[int, QByteArray]:  # noqa: N802
        return {
            _HEDGE_TIME_ROLE: QByteArray(b"time"),
            _HEDGE_SPOT_ROLE: QByteArray(b"spot"),
            _HEDGE_OPTION_VALUE_ROLE: QByteArray(b"optionValue"),
            _HEDGE_STOCK_UNITS_ROLE: QByteArray(b"stockUnits"),
            _HEDGE_TRADE_UNITS_ROLE: QByteArray(b"tradeUnits"),
            _HEDGE_CASH_ROLE: QByteArray(b"cashAccount"),
            _HEDGE_VALUE_ROLE: QByteArray(b"hedgeValue"),
            _HEDGE_COST_ROLE: QByteArray(b"transactionCost"),
        }

    def set_items(self, items: tuple[HedgeStepRow, ...]) -> None:
        self.beginResetModel()
        self._items = items
        self.endResetModel()


_FREQUENCY_CADENCE_ROLE = int(Qt.ItemDataRole.UserRole) + 1
_FREQUENCY_REPLICATES_ROLE = _FREQUENCY_CADENCE_ROLE + 1
_FREQUENCY_MEAN_ROLE = _FREQUENCY_CADENCE_ROLE + 2
_FREQUENCY_STD_ROLE = _FREQUENCY_CADENCE_ROLE + 3
_FREQUENCY_MAE_ROLE = _FREQUENCY_CADENCE_ROLE + 4
_FREQUENCY_RMSE_ROLE = _FREQUENCY_CADENCE_ROLE + 5


class HedgeFrequencyModel(QAbstractListModel):
    """Expose M3 aggregate evidence without conflating it with one path."""

    def __init__(self) -> None:
        super().__init__()
        self._items: tuple[HedgeFrequencyRow, ...] = ()

    def rowCount(  # noqa: N802
        self,
        parent: QModelIndex | QPersistentModelIndex = _INVALID_INDEX,
    ) -> int:
        return 0 if parent.isValid() else len(self._items)

    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        role: int = int(Qt.ItemDataRole.DisplayRole),
    ) -> object | None:
        if not index.isValid() or not 0 <= index.row() < len(self._items):
            return None
        item = self._items[index.row()]
        return {
            _FREQUENCY_CADENCE_ROLE: item.cadence,
            _FREQUENCY_REPLICATES_ROLE: item.replicates,
            _FREQUENCY_MEAN_ROLE: item.mean_error,
            _FREQUENCY_STD_ROLE: item.error_standard_deviation,
            _FREQUENCY_MAE_ROLE: item.mean_absolute_error,
            _FREQUENCY_RMSE_ROLE: item.root_mean_square_error,
        }.get(role)

    def roleNames(self) -> dict[int, QByteArray]:  # noqa: N802
        return {
            _FREQUENCY_CADENCE_ROLE: QByteArray(b"cadence"),
            _FREQUENCY_REPLICATES_ROLE: QByteArray(b"replicates"),
            _FREQUENCY_MEAN_ROLE: QByteArray(b"meanError"),
            _FREQUENCY_STD_ROLE: QByteArray(b"errorStandardDeviation"),
            _FREQUENCY_MAE_ROLE: QByteArray(b"meanAbsoluteError"),
            _FREQUENCY_RMSE_ROLE: QByteArray(b"rootMeanSquareError"),
        }

    def set_items(self, items: tuple[HedgeFrequencyRow, ...]) -> None:
        self.beginResetModel()
        self._items = items
        self.endResetModel()


_MARKET_CONTRACT_ROLE = int(Qt.ItemDataRole.UserRole) + 1
_MARKET_EXPIRY_ROLE = _MARKET_CONTRACT_ROLE + 1
_MARKET_STRIKE_ROLE = _MARKET_CONTRACT_ROLE + 2
_MARKET_RIGHT_ROLE = _MARKET_CONTRACT_ROLE + 3
_MARKET_BID_ROLE = _MARKET_CONTRACT_ROLE + 4
_MARKET_ASK_ROLE = _MARKET_CONTRACT_ROLE + 5
_MARKET_NORMALIZED_ROLE = _MARKET_CONTRACT_ROLE + 6
_MARKET_SPOT_ROLE = _MARKET_CONTRACT_ROLE + 7
_MARKET_IV_ROLE = _MARKET_CONTRACT_ROLE + 8
_MARKET_STATUS_ROLE = _MARKET_CONTRACT_ROLE + 9
_MARKET_DIAGNOSTIC_ROLE = _MARKET_CONTRACT_ROLE + 10


class MarketObservationModel(QAbstractListModel):
    """Expose raw/normalized/inferred M4 observation rows without backend graphs."""

    def __init__(self) -> None:
        super().__init__()
        self._items: tuple[MarketObservationRow, ...] = ()

    def rowCount(  # noqa: N802
        self,
        parent: QModelIndex | QPersistentModelIndex = _INVALID_INDEX,
    ) -> int:
        return 0 if parent.isValid() else len(self._items)

    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        role: int = int(Qt.ItemDataRole.DisplayRole),
    ) -> object | None:
        if not index.isValid() or not 0 <= index.row() < len(self._items):
            return None
        item = self._items[index.row()]
        return {
            _MARKET_CONTRACT_ROLE: item.contract_id,
            _MARKET_EXPIRY_ROLE: item.expiry,
            _MARKET_STRIKE_ROLE: item.strike,
            _MARKET_RIGHT_ROLE: item.right,
            _MARKET_BID_ROLE: item.bid,
            _MARKET_ASK_ROLE: item.ask,
            _MARKET_NORMALIZED_ROLE: item.normalized_price,
            _MARKET_SPOT_ROLE: item.observed_spot,
            _MARKET_IV_ROLE: item.implied_volatility,
            _MARKET_STATUS_ROLE: item.status,
            _MARKET_DIAGNOSTIC_ROLE: item.diagnostic,
        }.get(role)

    def roleNames(self) -> dict[int, QByteArray]:  # noqa: N802
        return {
            _MARKET_CONTRACT_ROLE: QByteArray(b"contractId"),
            _MARKET_EXPIRY_ROLE: QByteArray(b"expiry"),
            _MARKET_STRIKE_ROLE: QByteArray(b"strike"),
            _MARKET_RIGHT_ROLE: QByteArray(b"optionRight"),
            _MARKET_BID_ROLE: QByteArray(b"bid"),
            _MARKET_ASK_ROLE: QByteArray(b"ask"),
            _MARKET_NORMALIZED_ROLE: QByteArray(b"normalizedPrice"),
            _MARKET_SPOT_ROLE: QByteArray(b"observedSpot"),
            _MARKET_IV_ROLE: QByteArray(b"impliedVolatility"),
            _MARKET_STATUS_ROLE: QByteArray(b"status"),
            _MARKET_DIAGNOSTIC_ROLE: QByteArray(b"diagnostic"),
        }

    def set_items(self, items: tuple[MarketObservationRow, ...]) -> None:
        self.beginResetModel()
        self._items = items
        self.endResetModel()
