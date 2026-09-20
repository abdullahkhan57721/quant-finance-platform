"""Narrow tabular reporting values for downstream finance evidence exports."""

from __future__ import annotations

from dataclasses import dataclass

type ReportValue = str | int | float | bool | None


@dataclass(frozen=True, slots=True)
class ReportColumn:
    """One explicit exported column with human-readable units and meaning."""

    key: str
    label: str
    unit: str = ""
    description: str = ""

    @property
    def display_label(self) -> str:
        if not self.unit:
            return self.label
        return f"{self.label} [{self.unit}]"


@dataclass(frozen=True, slots=True)
class ReportField:
    """One scalar report-level assumption, convention, or provenance field."""

    key: str
    value: ReportValue
    unit: str = ""
    description: str = ""


@dataclass(frozen=True, slots=True)
class ReportTable:
    """A rectangular table over already-computed authoritative values."""

    name: str
    columns: tuple[ReportColumn, ...]
    rows: tuple[tuple[ReportValue, ...], ...]

    def __post_init__(self) -> None:
        name = self.name.strip()
        if not name or len(name) > 31:
            raise ValueError("report table name must contain 1-31 characters")
        if any(character in name for character in "[]:*?/\\"):
            raise ValueError("report table name contains an XLSX-forbidden character")
        if not self.columns:
            raise ValueError("report table must define at least one column")
        keys = tuple(column.key for column in self.columns)
        if len(keys) != len(set(keys)):
            raise ValueError("report column keys must be unique within one table")
        width = len(self.columns)
        if any(len(row) != width for row in self.rows):
            raise ValueError("every report row must match the declared column count")
        object.__setattr__(self, "name", name)


@dataclass(frozen=True, slots=True)
class TabularReport:
    """Concrete tabular export payload; not a quantitative result or document engine."""

    report_id: str
    title: str
    metadata: tuple[ReportField, ...]
    tables: tuple[ReportTable, ...]

    def __post_init__(self) -> None:
        report_id = self.report_id.strip()
        title = self.title.strip()
        if not report_id or not title:
            raise ValueError("report_id and title must be non-empty")
        if not self.tables:
            raise ValueError("tabular report must contain at least one table")
        metadata_keys = tuple(field.key for field in self.metadata)
        if len(metadata_keys) != len(set(metadata_keys)):
            raise ValueError("report metadata keys must be unique")
        table_names = tuple(table.name for table in self.tables)
        if len(table_names) != len(set(table_names)):
            raise ValueError("report table names must be unique")
        object.__setattr__(self, "report_id", report_id)
        object.__setattr__(self, "title", title)
