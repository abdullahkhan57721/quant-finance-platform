"""Curated PySide6 controller for UI1 + UI2 Black-Scholes Workbench flows."""

# PySide Property decorators are runtime descriptors whose stubs can look like
# redeclarations to strict Pyright when paired with Python property-style methods.
# pyright: reportRedeclaration=false

from __future__ import annotations

import json
from collections.abc import Callable

from PySide6.QtCore import Property, QObject, QThread, Signal, Slot

from qf_platform.application import (
    M2WorkbenchAnalysis,
    M2WorkbenchDraft,
    M2WorkbenchRequest,
    canonical_black_scholes_draft,
    compose_black_scholes_study,
    make_m2_workbench_request,
    run_m2_workbench,
    selected_method,
)
from qf_platform.application.black_scholes_study import (
    BlackScholesStudyComposition,
    BlackScholesStudyDraft,
)
from qf_platform.desktop.models import (
    GreekComparisonModel,
    PresentationRowModel,
    ValuationComparisonModel,
)
from qf_platform.presentation import (
    BlackScholesPresentation,
    M2WorkbenchPresentation,
    PlotData,
    build_black_scholes_presentation,
    build_m2_workbench_presentation,
)
from qf_platform.pricing import ValuationResult, evaluate


class _PricingWorker(QObject):
    """Retain the UI1 single-method execution path for source compatibility."""

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


class _M2Worker(QObject):
    """Execute one immutable UI2 analysis request outside the GUI thread."""

    completed = Signal(object)
    failed = Signal(str)

    def __init__(self, request: M2WorkbenchRequest) -> None:
        super().__init__()
        self._request = request

    @Slot()
    def run(self) -> None:
        try:
            analysis = run_m2_workbench(self._request)
        except Exception as exc:  # boundary converts execution failure into UI state
            self.failed.emit(f"{type(exc).__name__}: {exc}")
            return
        self.completed.emit(analysis)


class WorkbenchController(QObject):
    """Expose curated values/actions while keeping quantitative graphs private."""

    compositionChanged = Signal()
    runningChanged = Signal()
    resultsChanged = Signal()
    presentationChanged = Signal()
    statusChanged = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._composition: BlackScholesStudyComposition | None = None
        self._request: M2WorkbenchRequest | None = None
        self._analysis: M2WorkbenchAnalysis | None = None
        self._result: ValuationResult | None = None
        self._ui1_presentation: BlackScholesPresentation | None = None
        self._m2_presentation: M2WorkbenchPresentation | None = None
        self._inspector = PresentationRowModel()
        self._evidence = PresentationRowModel()
        self._compatibility = PresentationRowModel()
        self._result_rows = PresentationRowModel()
        self._provenance = PresentationRowModel()
        self._finite_difference = PresentationRowModel()
        self._valuation_comparison = ValuationComparisonModel()
        self._greek_comparison = GreekComparisonModel()
        self._thread: QThread | None = None
        self._worker: QObject | None = None
        self._status = "Create a Black-Scholes study or load the canonical example."
        self._defaults = canonical_black_scholes_draft()
        self._m2_defaults = M2WorkbenchDraft()

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

    @Property(str, constant=True)
    def defaultValuationMethod(self) -> str:  # noqa: N802
        return self._m2_defaults.valuation_method

    @Property(str, constant=True)
    def defaultCrrSteps(self) -> str:  # noqa: N802
        return self._m2_defaults.crr_steps

    @Property(str, constant=True)
    def defaultMonteCarloPaths(self) -> str:  # noqa: N802
        return self._m2_defaults.monte_carlo_paths

    @Property(str, constant=True)
    def defaultMonteCarloSeed(self) -> str:  # noqa: N802
        return self._m2_defaults.monte_carlo_seed

    @Property(str, constant=True)
    def defaultGreek(self) -> str:  # noqa: N802
        return self._m2_defaults.selected_greek

    @Property(str, constant=True)
    def defaultSpotBump(self) -> str:  # noqa: N802
        return self._m2_defaults.spot_bump

    @Property(str, constant=True)
    def defaultVolatilityBump(self) -> str:  # noqa: N802
        return self._m2_defaults.volatility_bump

    @Property(str, constant=True)
    def defaultRateBump(self) -> str:  # noqa: N802
        return self._m2_defaults.rate_bump

    @Property(str, constant=True)
    def defaultThetaDayBump(self) -> str:  # noqa: N802
        return self._m2_defaults.theta_day_bump

    @Property(bool, notify=compositionChanged)
    def compositionReady(self) -> bool:  # noqa: N802
        return self._composition is not None

    @Property(bool, notify=compositionChanged)
    def methodSupported(self) -> bool:  # noqa: N802
        if self._request is not None:
            return selected_method(self._request.config).supports(
                self._request.composition.problem
            )
        return self._composition is not None and self._composition.method_supported

    @Property(str, notify=compositionChanged)
    def selectedMethodLabel(self) -> str:  # noqa: N802
        if self._request is None:
            return "Black-Scholes analytic"
        return self._request.config.valuation_method.label

    @Property(bool, notify=runningChanged)
    def running(self) -> bool:
        return self._thread is not None

    @Property(str, notify=statusChanged)
    def status(self) -> str:
        return self._status

    @Property(bool, notify=resultsChanged)
    def hasResult(self) -> bool:  # noqa: N802
        return self._result is not None

    @Property(bool, notify=resultsChanged)
    def analysisReady(self) -> bool:  # noqa: N802
        return self._analysis is not None

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

    @Property(QObject, constant=True)
    def compatibilityModel(self) -> QObject:  # noqa: N802
        return self._compatibility

    @Property(QObject, constant=True)
    def resultModel(self) -> QObject:  # noqa: N802
        return self._result_rows

    @Property(QObject, constant=True)
    def provenanceModel(self) -> QObject:  # noqa: N802
        return self._provenance

    @Property(QObject, constant=True)
    def finiteDifferenceModel(self) -> QObject:  # noqa: N802
        return self._finite_difference

    @Property(QObject, constant=True)
    def valuationComparisonModel(self) -> QObject:  # noqa: N802
        return self._valuation_comparison

    @Property(QObject, constant=True)
    def greekComparisonModel(self) -> QObject:  # noqa: N802
        return self._greek_comparison

    @Property(str, notify=presentationChanged)
    def payoffPointsJson(self) -> str:  # noqa: N802
        if self._ui1_presentation is None:
            return "[]"
        return json.dumps(
            [
                {"underlying": point.underlying, "payoff": point.payoff}
                for point in self._ui1_presentation.payoff_points
            ],
            separators=(",", ":"),
        )

    @Property(str, notify=presentationChanged)
    def payoffPlotJson(self) -> str:  # noqa: N802
        return self._plot_json("payoff")

    @Property(str, notify=presentationChanged)
    def crrPlotJson(self) -> str:  # noqa: N802
        return self._plot_json("crr")

    @Property(str, notify=presentationChanged)
    def monteCarloPlotJson(self) -> str:  # noqa: N802
        return self._plot_json("monte_carlo")

    @Property(str, notify=presentationChanged)
    def greekPlotJson(self) -> str:  # noqa: N802
        return self._plot_json("greek")

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
        """Retain the UI1 financial-composition validation path."""
        if self.running:
            self._set_status("Quantitative work is already running.")
            return False
        try:
            composition = compose_black_scholes_study(
                _financial_draft(
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
            "Composition is structurally valid, but the analytic method is unsupported."
        )
        return False

    @Slot(
        str,
        str,
        str,
        str,
        str,
        str,
        str,
        str,
        str,
        str,
        str,
        str,
        str,
        str,
        str,
        str,
        str,
        result=bool,
    )
    def validateStudy(  # noqa: N802
        self,
        spot: str,
        strike: str,
        valuation_date: str,
        expiry: str,
        volatility: str,
        rate: str,
        carry: str,
        option_right: str,
        valuation_method: str,
        crr_steps: str,
        monte_carlo_paths: str,
        monte_carlo_seed: str,
        selected_greek: str,
        spot_bump: str,
        volatility_bump: str,
        rate_bump: str,
        theta_day_bump: str,
    ) -> bool:
        """Normalize UI2 financial and method drafts without running the studies."""
        if self.running:
            self._set_status("Quantitative work is already running.")
            return False
        try:
            request = _request(
                spot,
                strike,
                valuation_date,
                expiry,
                volatility,
                rate,
                carry,
                option_right,
                valuation_method,
                crr_steps,
                monte_carlo_paths,
                monte_carlo_seed,
                selected_greek,
                spot_bump,
                volatility_bump,
                rate_bump,
                theta_day_bump,
            )
        except (TypeError, ValueError) as exc:
            self._clear_authoritative_state()
            self._set_status(f"Study invalid: {exc}")
            return False
        self._activate_request(request)
        supported = selected_method(request.config).supports(
            request.composition.problem
        )
        if supported:
            self._set_status(
                f"Study valid; {request.config.valuation_method.label} is supported."
            )
        else:
            self._set_status(
                f"Study valid; {request.config.valuation_method.label} is unsupported "
                "for this configured pricing problem."
            )
        return supported

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
        """Retain the UI1 authoritative analytic pricing action."""
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
        self._start_worker(worker, self._pricing_completed)
        self._set_status(
            "Pricing with the authoritative Black-Scholes analytic method…"
        )
        return True

    @Slot(
        str,
        str,
        str,
        str,
        str,
        str,
        str,
        str,
        str,
        str,
        str,
        str,
        str,
        str,
        str,
        str,
        str,
        result=bool,
    )
    def runStudy(  # noqa: N802
        self,
        spot: str,
        strike: str,
        valuation_date: str,
        expiry: str,
        volatility: str,
        rate: str,
        carry: str,
        option_right: str,
        valuation_method: str,
        crr_steps: str,
        monte_carlo_paths: str,
        monte_carlo_seed: str,
        selected_greek: str,
        spot_bump: str,
        volatility_bump: str,
        rate_bump: str,
        theta_day_bump: str,
    ) -> bool:
        """Execute the concrete UI2 comparison/sensitivity request on QThread."""
        if not self.validateStudy(
            spot,
            strike,
            valuation_date,
            expiry,
            volatility,
            rate,
            carry,
            option_right,
            valuation_method,
            crr_steps,
            monte_carlo_paths,
            monte_carlo_seed,
            selected_greek,
            spot_bump,
            volatility_bump,
            rate_bump,
            theta_day_bump,
        ):
            return False
        request = self._request
        if request is None:
            return False
        worker = _M2Worker(request)
        self._start_worker(worker, self._study_completed)
        self._set_status(
            "Running M2 valuation comparison, convergence, uncertainty, and Greeks…"
        )
        return True

    @Slot(object)
    def _pricing_completed(self, result: object) -> None:
        if not isinstance(result, ValuationResult) or self._composition is None:
            self._set_status("Pricing returned an unexpected result payload.")
            return
        self._result = result
        self._apply_ui1_presentation(
            build_black_scholes_presentation(self._composition, result)
        )
        self.resultsChanged.emit()
        self._set_status("Pricing complete; displaying immutable valuation evidence.")

    @Slot(object)
    def _study_completed(self, payload: object) -> None:
        request = self._request
        if not isinstance(payload, M2WorkbenchAnalysis) or request is None:
            self._set_status("UI2 analysis returned an unexpected payload.")
            return
        self._analysis = payload
        self._result = payload.selected_valuation.result
        analytic = next(
            run for run in payload.valuations if run.method.value == "analytic"
        )
        self._apply_ui1_presentation(
            build_black_scholes_presentation(
                request.composition,
                analytic.result,
            )
        )
        self._apply_m2_presentation(build_m2_workbench_presentation(request, payload))
        self.resultsChanged.emit()
        self._set_status(
            "UI2 study complete; comparison, uncertainty, Greeks, and diagnostics "
            "are authoritative backend-derived evidence."
        )

    @Slot(str)
    def _worker_failed(self, message: str) -> None:
        self._set_status(f"Quantitative execution failed: {message}")

    @Slot()
    def _worker_finished(self) -> None:
        self._worker = None
        self._thread = None
        self.runningChanged.emit()

    def _start_worker(
        self,
        worker: _PricingWorker | _M2Worker,
        completed_slot: Callable[[object], None],
    ) -> None:
        thread = QThread(self)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.completed.connect(completed_slot)
        worker.failed.connect(self._worker_failed)
        worker.completed.connect(thread.quit)
        worker.failed.connect(thread.quit)
        worker.completed.connect(worker.deleteLater)
        worker.failed.connect(worker.deleteLater)
        thread.finished.connect(self._worker_finished)
        thread.finished.connect(thread.deleteLater)
        self._worker = worker
        self._thread = thread
        self.runningChanged.emit()
        thread.start()

    def _activate_composition(
        self,
        composition: BlackScholesStudyComposition,
    ) -> None:
        self._composition = composition
        self._request = None
        self._analysis = None
        self._result = None
        self._clear_m2_presentation()
        self._apply_ui1_presentation(build_black_scholes_presentation(composition))
        self.compositionChanged.emit()
        self.resultsChanged.emit()

    def _activate_request(self, request: M2WorkbenchRequest) -> None:
        self._composition = request.composition
        self._request = request
        self._analysis = None
        self._result = None
        self._clear_m2_presentation()
        self._apply_ui1_presentation(
            build_black_scholes_presentation(request.composition)
        )
        self.compositionChanged.emit()
        self.resultsChanged.emit()

    def _clear_authoritative_state(self) -> None:
        self._composition = None
        self._request = None
        self._analysis = None
        self._result = None
        self._ui1_presentation = None
        self._inspector.set_items(())
        self._evidence.set_items(())
        self._clear_m2_presentation()
        self.compositionChanged.emit()
        self.resultsChanged.emit()
        self.presentationChanged.emit()

    def _clear_m2_presentation(self) -> None:
        self._m2_presentation = None
        self._compatibility.set_items(())
        self._result_rows.set_items(())
        self._provenance.set_items(())
        self._finite_difference.set_items(())
        self._valuation_comparison.set_items(())
        self._greek_comparison.set_items(())
        self.presentationChanged.emit()

    def _apply_ui1_presentation(
        self,
        presentation: BlackScholesPresentation,
    ) -> None:
        self._ui1_presentation = presentation
        self._inspector.set_items(presentation.inspector_rows)
        self._evidence.set_items(presentation.evidence_rows)
        self.presentationChanged.emit()

    def _apply_m2_presentation(
        self,
        presentation: M2WorkbenchPresentation,
    ) -> None:
        self._m2_presentation = presentation
        self._compatibility.set_items(presentation.compatibility_rows)
        self._result_rows.set_items(presentation.result_rows)
        self._provenance.set_items(presentation.provenance_rows)
        self._finite_difference.set_items(presentation.finite_difference_rows)
        self._valuation_comparison.set_items(presentation.valuation_rows)
        self._greek_comparison.set_items(presentation.greek_rows)
        self.presentationChanged.emit()

    def _plot_json(self, name: str) -> str:
        presentation = self._m2_presentation
        if presentation is None:
            return "{}"
        plots = {
            "payoff": presentation.payoff_plot,
            "crr": presentation.crr_plot,
            "monte_carlo": presentation.monte_carlo_plot,
            "greek": presentation.greek_plot,
        }
        return _serialize_plot(plots[name])

    def _set_status(self, value: str) -> None:
        self._status = value
        self.statusChanged.emit()


def _financial_draft(
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


def _request(
    spot: str,
    strike: str,
    valuation_date: str,
    expiry: str,
    volatility: str,
    rate: str,
    carry: str,
    option_right: str,
    valuation_method: str,
    crr_steps: str,
    monte_carlo_paths: str,
    monte_carlo_seed: str,
    selected_greek: str,
    spot_bump: str,
    volatility_bump: str,
    rate_bump: str,
    theta_day_bump: str,
) -> M2WorkbenchRequest:
    composition = compose_black_scholes_study(
        _financial_draft(
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
    return make_m2_workbench_request(
        composition,
        M2WorkbenchDraft(
            valuation_method=valuation_method,
            crr_steps=crr_steps,
            monte_carlo_paths=monte_carlo_paths,
            monte_carlo_seed=monte_carlo_seed,
            selected_greek=selected_greek,
            spot_bump=spot_bump,
            volatility_bump=volatility_bump,
            rate_bump=rate_bump,
            theta_day_bump=theta_day_bump,
        ),
    )


def _serialize_plot(plot: PlotData) -> str:
    return json.dumps(
        {
            "title": plot.title,
            "xLabel": plot.x_label,
            "yLabel": plot.y_label,
            "series": [
                {
                    "key": series.key,
                    "label": series.label,
                    "points": [
                        {
                            "x": point.x,
                            "y": point.y,
                            "lower": point.lower,
                            "upper": point.upper,
                        }
                        for point in series.points
                    ],
                }
                for series in plot.series
            ],
        },
        separators=(",", ":"),
    )


__all__ = ["WorkbenchController"]
