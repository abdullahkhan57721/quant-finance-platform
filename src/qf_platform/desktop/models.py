"""Curated Qt models for renderer-neutral presentation values."""

from __future__ import annotations

from PySide6.QtCore import QAbstractListModel, QByteArray, QModelIndex, Qt

from qf_platform.presentation import PresentationRow

_LABEL_ROLE = int(Qt.ItemDataRole.UserRole) + 1
_VALUE_ROLE = _LABEL_ROLE + 1
_DETAIL_ROLE = _LABEL_ROLE + 2
_STATUS_ROLE = _LABEL_ROLE + 3
_INVALID_INDEX = QModelIndex()


class PresentationRowModel(QAbstractListModel):
    """Expose presentation rows without exposing finance-domain object graphs."""

    def __init__(self) -> None:
        super().__init__()
        self._items: tuple[PresentationRow, ...] = ()

    def rowCount(self, parent: QModelIndex = _INVALID_INDEX) -> int:  # noqa: N802
        if parent.isValid():
            return 0
        return len(self._items)

    def data(
        self,
        index: QModelIndex,
        role: int = int(Qt.ItemDataRole.DisplayRole),
    ) -> object | None:
        if not index.isValid() or not 0 <= index.row() < len(self._items):
            return None
        item = self._items[index.row()]
        if role == _LABEL_ROLE:
            return item.label
        if role == _VALUE_ROLE:
            return item.value
        if role == _DETAIL_ROLE:
            return item.detail
        if role == _STATUS_ROLE:
            return item.status
        return None

    def roleNames(self) -> dict[int, QByteArray]:  # noqa: N802
        return {
            _LABEL_ROLE: QByteArray(b"label"),
            _VALUE_ROLE: QByteArray(b"value"),
            _DETAIL_ROLE: QByteArray(b"detail"),
            _STATUS_ROLE: QByteArray(b"status"),
        }

    def set_items(self, items: tuple[PresentationRow, ...]) -> None:
        """Replace rows atomically after Python application semantics prepare them."""
        self.beginResetModel()
        self._items = items
        self.endResetModel()
