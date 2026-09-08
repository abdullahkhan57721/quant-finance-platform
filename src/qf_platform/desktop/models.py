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
    PresentationRow,
    ValuationComparisonRow,
)

_LABEL_ROLE = int(Qt.ItemDataRole.UserRole) + 1
_VALUE_ROLE = _LABEL_ROLE + 1
_DETAIL_ROLE = _LABEL_ROLE + 2
_STATUS_ROLE = _LABEL_ROLE + 3
_INVALID_INDEX: QModelIndex | QPersistentModelIndex = QModelIndex()


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
