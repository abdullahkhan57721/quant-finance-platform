"""Thin PySide6 controller for the UI1 Black-Scholes vertical."""

# PySide Property decorators are runtime descriptors whose stubs can look like
# redeclarations to strict Pyright when paired with Python property-style methods.
# pyright: reportRedeclaration=false

from __future__ import annotations

import json

from PySide6.QtCore import Property, QObject, QThread, Signal, Slot

from qf_platform.application import (
    BlackScholesStudyComposition,
    BlackScholesStudyDraft,
    canonical_black_scholes_draft,
    compose_black_scholes_study,
)
from qf_platform.desktop.models import PresentationRowModel
from qf_platform.presentation import (
    BlackScholesPresentation,
    build_black_scholes_presentation,
)
from qf_platform.pricing import ValuationResult, evaluate


class _PricingWorker(QObject):
    """Evaluate one immutable M1 composition outside the GUI thread."""

    completed = Signal(object)
    failed = Signal(str)

    def __init__(self, composition: BlackScholesStudyComposition) -> None:
        super().__init__()
        self._composition = composition

    @Slot()
    def run(self) -> None:
        try:
            result = evaluate(self._composition.problem, self._composition.method)
        except Exception as exc:  # boundary converts execution failure into UI state
            self.failed.emit(f"{type(exc).__name__}: {exc}")
            return
        self.completed.emit(result)


class WorkbenchController(QObject):
    """Expose curated values/actions while keeping M1 objects private to Python."""

    compositionChanged = Signal()
    runningChanged = Signal()
    resultsChanged = Signal()
    presentationChanged = Signal()
    statusChanged = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._composition: BlackScholesStudyComposition | None = None
        self._result: ValuationResult | None = None
        self._presentation: BlackScholesPresentation | None = None
        self._inspector = PresentationRowModel()
        self._evidence = PresentationRowModel()
        self._thread: QThread | None = None
        self._worker: _PricingWorker | None = None
        self._status = "Create a Black-Scholes study or load the canonical example."
        self._defaults = canonical_black_scholes_draft()

    @Property(str, constant=True)
    def defaultSpot(self) -> str:  # noqa: N802
        return self._defaults.spot

    @Property(str, constant=True)
    def defaultStrike(self) -> str:  # noqa: N802
        return self._defaults.strike

    @Property(str, constant=True)
    def defaultValuationDate(self) -> str:  # noqa: N802
        return self._defaults.valuation_date

    @Property(str, constant=True)
    def defaultExpiry(self) -> str:  # noqa: N802
        return self._defaults.expiry

    @Property(str, constant=True)
    def defaultVolatility(self) -> str:  # noqa: N802
        return self._defaults.annualized_volatility

    @Property(str, constant=True)
    def defaultRate(self) -> str:  # noqa: N802
        return self._defaults.continuously_compounded_rate

    @Property(str, constant=True)
    def defaultCarry(self) -> str:  # noqa: N802
        return self._defaults.continuous_dividend_yield

    @Property(str, constant=True)
    def defaultOptionRight(self) -> str:  # noqa: N802
        return self._defaults.option_right

    @Property(bool, notify=compositionChanged)
    def compositionReady(self) -> bool:  # noqa: N802
        return self._composition is not None

    @Property(bool, notify=compositionChanged)
    def methodSupported(self) -> bool:  # noqa: N802
        return self._composition is not None and self._composition.method_supported

    @Property(bool, notify=runningChanged)
    def running(self) -> bool:
        return self._thread is not None

    @Property(str, notify=statusChanged)
    def status(self) -> str:
        return self._status

    @Property(bool, notify=resultsChanged)
    def hasResult(self) -> bool:  # noqa: N802
        return self._result is not None

    @Property(str, notify=resultsChanged)
    def presentValue(self) -> str:  # noqa: N802
        if self._result is None:
            return "—"
        return f"{self._result.present_value:.12g}"

    @Property(QObject, constant=True)
    def inspectorModel(self) -> QObject:  # noqa: N802
        return self._inspector

    @Property(QObject, constant=True)
    def evidenceModel(self) -> QObject:  # noqa: N802
        return self._evidence

    @Property(str, notify=presentationChanged)
    def payoffPointsJson(self) -> str:  # noqa: N802
        if self._presentation is None:
            return "[]"
        return json.dumps(
            [
                {"underlying": point.underlying, "payoff": point.payoff}
                for point in self._presentation.payoff_points
            ],
            separators=(",", ":"),
        )

    @Slot(str, str, str, str, str, str, str, str, result=bool)
    def validateDraft(  # noqa: N802
        self,
        spot: str,
        strike: str,
        valuation_date: str,
        expiry: str,
        volatility: str,
        rate: str,
        carry: str,
        option_right: str,
    ) -> bool:
        """Normalize transient UI inputs into immutable M1 semantics."""
        if self.running:
            self._set_status("Pricing is already running.")
            return False
        try:
            composition = compose_black_scholes_study(
                _draft(
                    spot,
                    strike,
                    valuation_date,
                    expiry,
                    volatility,
                    rate,
                    carry,
                    option_right,
                )
            )
        except (TypeError, ValueError) as exc:
            self._clear_authoritative_state()
            self._set_status(f"Composition invalid: {exc}")
            return False
        self._activate_composition(composition)
        if composition.method_supported:
            self._set_status(
                "Composition valid; Black-Scholes analytic is supported and ready."
            )
            return True
        self._set_status(
            "Composition is structurally valid, but the selected analytic method is unsupported."
        )
        return False

    @Slot(str, str, str, str, str, str, str, str, result=bool)
    def priceDraft(  # noqa: N802
        self,
        spot: str,
        strike: str,
        valuation_date: str,
        expiry: str,
        volatility: str,
        rate: str,
        carry: str,
        option_right: str,
    ) -> bool:
        """Normalize current draft and execute the supported M1 method on QThread."""
        if not self.validateDraft(
            spot,
            strike,
            valuation_date,
            expiry,
            volatility,
            rate,
            carry,
            option_right,
        ):
            return False
        composition = self._composition
        if composition is None or not composition.method_supported:
            return False

        worker = _PricingWorker(composition)
        thread = QThread(self)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.completed.connect(self._pricing_completed)
        worker.failed.connect(self._pricing_failed)
        worker.completed.connect(thread.quit)
        worker.failed.connect(thread.quit)
        worker.completed.connect(worker.deleteLater)
        worker.failed.connect(worker.deleteLater)
        thread.finished.connect(self._worker_finished)
        thread.finished.connect(thread.deleteLater)
        self._worker = worker
        self._thread = thread
        self.runningChanged.emit()
        self._set_status("Pricing with the authoritative M1 Black-Scholes method…")
        thread.start()
        return True

    @Slot(object)
    def _pricing_completed(self, result: object) -> None:
        if not isinstance(result, ValuationResult) or self._composition is None:
            self._set_status("Pricing returned an unexpected result payload.")
            return
        self._result = result
        self._apply_presentation(
            build_black_scholes_presentation(self._composition, result)
        )
        self.resultsChanged.emit()
        self._set_status(
            "Pricing complete; Results display immutable ValuationResult evidence."
        )

    @Slot(str)
    def _pricing_failed(self, message: str) -> None:
        self._set_status(f"Pricing failed: {message}")

    @Slot()
    def _worker_finished(self) -> None:
        self._worker = None
        self._thread = None
        self.runningChanged.emit()

    def _activate_composition(
        self,
        composition: BlackScholesStudyComposition,
    ) -> None:
        self._composition = composition
        self._result = None
        self._apply_presentation(build_black_scholes_presentation(composition))
        self.compositionChanged.emit()
        self.resultsChanged.emit()

    def _clear_authoritative_state(self) -> None:
        self._composition = None
        self._result = None
        self._presentation = None
        self._inspector.set_items(())
        self._evidence.set_items(())
        self.compositionChanged.emit()
        self.resultsChanged.emit()
        self.presentationChanged.emit()

    def _apply_presentation(self, presentation: BlackScholesPresentation) -> None:
        self._presentation = presentation
        self._inspector.set_items(presentation.inspector_rows)
        self._evidence.set_items(presentation.evidence_rows)
        self.presentationChanged.emit()

    def _set_status(self, value: str) -> None:
        self._status = value
        self.statusChanged.emit()


def _draft(
    spot: str,
    strike: str,
    valuation_date: str,
    expiry: str,
    volatility: str,
    rate: str,
    carry: str,
    option_right: str,
) -> BlackScholesStudyDraft:
    return BlackScholesStudyDraft(
        spot=spot,
        strike=strike,
        valuation_date=valuation_date,
        expiry=expiry,
        annualized_volatility=volatility,
        continuously_compounded_rate=rate,
        continuous_dividend_yield=carry,
        option_right=option_right,
    )


__all__ = ["WorkbenchController"]
