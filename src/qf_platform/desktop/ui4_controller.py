"""Curated PySide6 controller extensions for concrete UI4 Heston workflows."""

# PySide Property decorators are runtime descriptors whose stubs can look like
# redeclarations to strict Pyright when paired with Python property-style methods.
# pyright: reportRedeclaration=false

from __future__ import annotations

import json
from collections.abc import Callable

from PySide6.QtCore import Property, QObject, QThread, Signal, Slot

from qf_platform.application.ui4_heston import (
    HestonCalibrationDraft,
    HestonCalibrationWorkbenchAnalysis,
    HestonCalibrationWorkbenchRequest,
    HestonPricingAnalysis,
    HestonPricingDraft,
    HestonPricingRequest,
    canonical_m6_market_reference,
    make_heston_calibration_request,
    make_heston_pricing_request,
    run_heston_calibration,
    run_heston_pricing,
)
from qf_platform.desktop.models import PresentationRowModel
from qf_platform.desktop.ui3_controller import (
    WorkbenchController as UI3WorkbenchController,
)
from qf_platform.presentation.plotting import PlotData
from qf_platform.presentation.ui4_heston import (
    HestonCalibrationPresentation,
    HestonPricingPresentation,
    M6MarketReferencePresentation,
    build_heston_calibration_presentation,
    build_heston_pricing_presentation,
    build_m6_market_reference_presentation,
)


class _HestonPricingWorker(QObject):
    """Execute one immutable UI4 Heston pricing request outside the GUI thread."""

    completed = Signal(int, object)
    failed = Signal(int, str)

    def __init__(self, job_id: int, request: HestonPricingRequest) -> None:
        super().__init__()
        self._job_id = job_id
        self._request = request

    @Slot()
    def run(self) -> None:
        try:
            analysis = run_heston_pricing(self._request)
        except Exception as exc:  # boundary converts execution failure into UI state
            self.failed.emit(self._job_id, f"{type(exc).__name__}: {exc}")
            return
        self.completed.emit(self._job_id, analysis)


class _HestonCalibrationWorker(QObject):
    """Execute one immutable UI4 calibration request outside the GUI thread."""

    completed = Signal(int, object)
    failed = Signal(int, str)

    def __init__(
        self,
        job_id: int,
        request: HestonCalibrationWorkbenchRequest,
    ) -> None:
        super().__init__()
        self._job_id = job_id
        self._request = request

    @Slot()
    def run(self) -> None:
        try:
            analysis = run_heston_calibration(self._request)
        except Exception as exc:  # boundary converts execution failure into UI state
            self.failed.emit(self._job_id, f"{type(exc).__name__}: {exc}")
            return
        self.completed.emit(self._job_id, analysis)


class WorkbenchController(UI3WorkbenchController):
    """Extend UI3 with Heston pricing and calibration without flattening semantics."""

    hestonChanged = Signal()
    calibrationChanged = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._heston_request: HestonPricingRequest | None = None
        self._heston_analysis: HestonPricingAnalysis | None = None
        self._heston_presentation: HestonPricingPresentation | None = None
        self._calibration_request: HestonCalibrationWorkbenchRequest | None = None
        self._calibration_analysis: HestonCalibrationWorkbenchAnalysis | None = None
        self._calibration_presentation: HestonCalibrationPresentation | None = None
        self._m6_market_presentation: M6MarketReferencePresentation = (
            build_m6_market_reference_presentation(canonical_m6_market_reference())
        )

        self._heston_model = PresentationRowModel()
        self._heston_parameters = PresentationRowModel()
        self._heston_results = PresentationRowModel()
        self._heston_fourier = PresentationRowModel()
        self._heston_monte_carlo = PresentationRowModel()
        self._heston_inspector = PresentationRowModel()

        self._calibration_problem = PresentationRowModel()
        self._calibration_truth = PresentationRowModel()
        self._calibration_runs = PresentationRowModel()
        self._calibration_residuals = PresentationRowModel()
        self._calibration_conditioning = PresentationRowModel()
        self._calibration_inspector = PresentationRowModel()

        self._m6_market_summary = PresentationRowModel()
        self._m6_market_provenance = PresentationRowModel()
        self._m6_market_starts = PresentationRowModel()
        self._m6_market_results = PresentationRowModel()
        self._m6_market_conditioning = PresentationRowModel()
        self._apply_m6_market_reference(self._m6_market_presentation)

        self._heston_defaults = HestonPricingDraft()
        self._calibration_defaults = HestonCalibrationDraft()

        self._ui4_job_sequence = 0
        self._ui4_active_job_id: int | None = None
        self._ui4_active_kind = ""
        self._ui4_active_valid = True

    @Property(str, constant=True)
    def defaultHestonSpot(self) -> str:  # noqa: N802
        return self._heston_defaults.spot

    @Property(str, constant=True)
    def defaultHestonStrike(self) -> str:  # noqa: N802
        return self._heston_defaults.strike

    @Property(str, constant=True)
    def defaultHestonValuationDate(self) -> str:  # noqa: N802
        return self._heston_defaults.valuation_date

    @Property(str, constant=True)
    def defaultHestonExpiry(self) -> str:  # noqa: N802
        return self._heston_defaults.expiry

    @Property(str, constant=True)
    def defaultHestonRate(self) -> str:  # noqa: N802
        return self._heston_defaults.continuously_compounded_rate

    @Property(str, constant=True)
    def defaultHestonCarry(self) -> str:  # noqa: N802
        return self._heston_defaults.continuous_dividend_yield

    @Property(str, constant=True)
    def defaultHestonOptionRight(self) -> str:  # noqa: N802
        return self._heston_defaults.option_right

    @Property(str, constant=True)
    def defaultHestonInitialVariance(self) -> str:  # noqa: N802
        return self._heston_defaults.initial_variance

    @Property(str, constant=True)
    def defaultHestonKappa(self) -> str:  # noqa: N802
        return self._heston_defaults.mean_reversion_speed

    @Property(str, constant=True)
    def defaultHestonTheta(self) -> str:  # noqa: N802
        return self._heston_defaults.long_run_variance

    @Property(str, constant=True)
    def defaultHestonXi(self) -> str:  # noqa: N802
        return self._heston_defaults.volatility_of_variance

    @Property(str, constant=True)
    def defaultHestonRho(self) -> str:  # noqa: N802
        return self._heston_defaults.correlation

    @Property(str, constant=True)
    def defaultHestonFourierLower(self) -> str:  # noqa: N802
        return self._heston_defaults.fourier_lower_bound

    @Property(str, constant=True)
    def defaultHestonFourierUpper(self) -> str:  # noqa: N802
        return self._heston_defaults.fourier_upper_bound

    @Property(str, constant=True)
    def defaultHestonFourierIntervals(self) -> str:  # noqa: N802
        return self._heston_defaults.fourier_intervals

    @Property(str, constant=True)
    def defaultHestonMonteCarloPaths(self) -> str:  # noqa: N802
        return self._heston_defaults.monte_carlo_paths

    @Property(str, constant=True)
    def defaultHestonMonteCarloSteps(self) -> str:  # noqa: N802
        return self._heston_defaults.monte_carlo_time_steps

    @Property(str, constant=True)
    def defaultHestonMonteCarloSeed(self) -> str:  # noqa: N802
        return self._heston_defaults.monte_carlo_seed

    @Property(str, constant=True)
    def defaultCalibrationInitialVariance(self) -> str:  # noqa: N802
        return self._calibration_defaults.initial_variance

    @Property(str, constant=True)
    def defaultCalibrationKappa(self) -> str:  # noqa: N802
        return self._calibration_defaults.mean_reversion_speed

    @Property(str, constant=True)
    def defaultCalibrationTheta(self) -> str:  # noqa: N802
        return self._calibration_defaults.long_run_variance

    @Property(str, constant=True)
    def defaultCalibrationXi(self) -> str:  # noqa: N802
        return self._calibration_defaults.volatility_of_variance

    @Property(str, constant=True)
    def defaultCalibrationRho(self) -> str:  # noqa: N802
        return self._calibration_defaults.correlation

    @Property(str, constant=True)
    def defaultCalibrationMaxEvaluations(self) -> str:  # noqa: N802
        return self._calibration_defaults.max_function_evaluations

    @Property(str, constant=True)
    def defaultCalibrationFourierIntervals(self) -> str:  # noqa: N802
        return self._calibration_defaults.fourier_intervals

    @Property(bool, notify=hestonChanged)
    def hestonAnalysisReady(self) -> bool:  # noqa: N802
        return self._heston_analysis is not None

    @Property(bool, notify=calibrationChanged)
    def calibrationAnalysisReady(self) -> bool:  # noqa: N802
        return self._calibration_analysis is not None

    @Property(QObject, constant=True)
    def hestonModelModel(self) -> QObject:  # noqa: N802
        return self._heston_model

    @Property(QObject, constant=True)
    def hestonParameterModel(self) -> QObject:  # noqa: N802
        return self._heston_parameters

    @Property(QObject, constant=True)
    def hestonResultModel(self) -> QObject:  # noqa: N802
        return self._heston_results

    @Property(QObject, constant=True)
    def hestonFourierModel(self) -> QObject:  # noqa: N802
        return self._heston_fourier

    @Property(QObject, constant=True)
    def hestonMonteCarloModel(self) -> QObject:  # noqa: N802
        return self._heston_monte_carlo

    @Property(QObject, constant=True)
    def hestonInspectorModel(self) -> QObject:  # noqa: N802
        return self._heston_inspector

    @Property(QObject, constant=True)
    def calibrationProblemModel(self) -> QObject:  # noqa: N802
        return self._calibration_problem

    @Property(QObject, constant=True)
    def calibrationTruthModel(self) -> QObject:  # noqa: N802
        return self._calibration_truth

    @Property(QObject, constant=True)
    def calibrationRunModel(self) -> QObject:  # noqa: N802
        return self._calibration_runs

    @Property(QObject, constant=True)
    def calibrationResidualModel(self) -> QObject:  # noqa: N802
        return self._calibration_residuals

    @Property(QObject, constant=True)
    def calibrationConditioningModel(self) -> QObject:  # noqa: N802
        return self._calibration_conditioning

    @Property(QObject, constant=True)
    def calibrationInspectorModel(self) -> QObject:  # noqa: N802
        return self._calibration_inspector

    @Property(QObject, constant=True)
    def m6MarketSummaryModel(self) -> QObject:  # noqa: N802
        return self._m6_market_summary

    @Property(QObject, constant=True)
    def m6MarketProvenanceModel(self) -> QObject:  # noqa: N802
        return self._m6_market_provenance

    @Property(QObject, constant=True)
    def m6MarketStartModel(self) -> QObject:  # noqa: N802
        return self._m6_market_starts

    @Property(QObject, constant=True)
    def m6MarketResultModel(self) -> QObject:  # noqa: N802
        return self._m6_market_results

    @Property(QObject, constant=True)
    def m6MarketConditioningModel(self) -> QObject:  # noqa: N802
        return self._m6_market_conditioning

    @Property(str, notify=hestonChanged)
    def hestonMethodComparisonPlotJson(self) -> str:  # noqa: N802
        presentation = self._heston_presentation
        return "{}" if presentation is None else _serialize_plot(
            presentation.method_comparison_plot
        )

    @Property(str, notify=hestonChanged)
    def hestonFourierStabilityPlotJson(self) -> str:  # noqa: N802
        presentation = self._heston_presentation
        return "{}" if presentation is None else _serialize_plot(
            presentation.fourier_stability_plot
        )

    @Property(str, notify=calibrationChanged)
    def calibrationParameterErrorPlotJson(self) -> str:  # noqa: N802
        presentation = self._calibration_presentation
        return "{}" if presentation is None else _serialize_plot(
            presentation.parameter_error_plot
        )

    @Property(str, notify=calibrationChanged)
    def calibrationResidualPlotJson(self) -> str:  # noqa: N802
        presentation = self._calibration_presentation
        return "{}" if presentation is None else _serialize_plot(
            presentation.residual_plot
        )

    @Property(str, notify=calibrationChanged)
    def calibrationObjectivePlotJson(self) -> str:  # noqa: N802
        presentation = self._calibration_presentation
        return "{}" if presentation is None else _serialize_plot(
            presentation.objective_plot
        )

    @Property(str, constant=True)
    def m6MarketResidualPlotJson(self) -> str:  # noqa: N802
        return _serialize_plot(self._m6_market_presentation.residual_plot)

    @Property(str, constant=True)
    def m6MarketObjectivePlotJson(self) -> str:  # noqa: N802
        return _serialize_plot(self._m6_market_presentation.objective_plot)

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
        str,
        result=bool,
    )
    def runHestonPricing(  # noqa: N802
        self,
        spot: str,
        strike: str,
        valuation_date: str,
        expiry: str,
        rate: str,
        carry: str,
        option_right: str,
        initial_variance: str,
        kappa: str,
        theta: str,
        xi: str,
        rho: str,
        fourier_lower: str,
        fourier_upper: str,
        fourier_intervals: str,
        monte_carlo_paths: str,
        monte_carlo_steps: str,
        monte_carlo_seed: str,
    ) -> bool:
        """Normalize and execute one concrete M5 Heston pricing comparison."""

        if self.running:
            self._set_status("Quantitative work is already running.")
            return False
        try:
            request = make_heston_pricing_request(
                HestonPricingDraft(
                    spot=spot,
                    strike=strike,
                    valuation_date=valuation_date,
                    expiry=expiry,
                    continuously_compounded_rate=rate,
                    continuous_dividend_yield=carry,
                    option_right=option_right,
                    initial_variance=initial_variance,
                    mean_reversion_speed=kappa,
                    long_run_variance=theta,
                    volatility_of_variance=xi,
                    correlation=rho,
                    fourier_lower_bound=fourier_lower,
                    fourier_upper_bound=fourier_upper,
                    fourier_intervals=fourier_intervals,
                    monte_carlo_paths=monte_carlo_paths,
                    monte_carlo_time_steps=monte_carlo_steps,
                    monte_carlo_seed=monte_carlo_seed,
                )
            )
        except (TypeError, ValueError) as exc:
            self._clear_heston_presentation()
            self._set_status(f"Heston pricing study invalid: {exc}")
            return False

        self._heston_request = request
        self._heston_analysis = None
        self._clear_heston_presentation()
        job_id = self._begin_ui4_job("heston")
        worker = _HestonPricingWorker(job_id, request)
        self._start_ui4_worker(worker, self._heston_completed)
        self._set_status(
            "Running M5 Heston Fourier + seeded Monte Carlo outside the GUI thread…"
        )
        return True

    @Slot(str, str, str, str, str, str, str, str, result=bool)
    def runHestonCalibration(  # noqa: N802
        self,
        mode: str,
        initial_variance: str,
        kappa: str,
        theta: str,
        xi: str,
        rho: str,
        max_function_evaluations: str,
        fourier_intervals: str,
    ) -> bool:
        """Run one concrete synthetic M6 calibration/identifiability study."""

        if self.running:
            self._set_status("Quantitative work is already running.")
            return False
        try:
            request = make_heston_calibration_request(
                mode,
                HestonCalibrationDraft(
                    initial_variance=initial_variance,
                    mean_reversion_speed=kappa,
                    long_run_variance=theta,
                    volatility_of_variance=xi,
                    correlation=rho,
                    max_function_evaluations=max_function_evaluations,
                    fourier_intervals=fourier_intervals,
                ),
            )
        except (TypeError, ValueError) as exc:
            self._clear_calibration_presentation()
            self._set_status(f"Heston calibration study invalid: {exc}")
            return False

        self._calibration_request = request
        self._calibration_analysis = None
        self._clear_calibration_presentation()
        job_id = self._begin_ui4_job("calibration")
        worker = _HestonCalibrationWorker(job_id, request)
        self._start_ui4_worker(worker, self._calibration_completed)
        self._set_status(
            "Running M6 price-space Heston calibration outside the GUI thread…"
        )
        return True

    @Slot(str)
    def invalidateUi4Result(self, workspace: str) -> None:  # noqa: N802
        """Reject an in-flight or displayed result after its relevant draft changes."""

        normalized = workspace.strip().lower()
        if normalized == "heston":
            self._heston_analysis = None
            self._clear_heston_presentation()
        elif normalized == "calibration":
            self._calibration_analysis = None
            self._clear_calibration_presentation()
        else:
            return
        if self._ui4_active_kind == normalized:
            self._ui4_active_valid = False
            if self.running:
                self._set_status(
                    "Inputs changed while quantitative work was running; "
                    "the completed stale result will be discarded."
                )

    @Slot(int, object)
    def _heston_completed(self, job_id: int, payload: object) -> None:
        if not self._accept_ui4_result(job_id, "heston"):
            self._set_status(
                "Heston pricing finished, but its inputs changed; stale result discarded."
            )
            return
        request = self._heston_request
        if not isinstance(payload, HestonPricingAnalysis) or request is None:
            self._set_status("UI4 Heston pricing returned an unexpected payload.")
            return
        self._heston_analysis = payload
        self._apply_heston_presentation(
            build_heston_pricing_presentation(request, payload)
        )
        self._set_status(
            "Heston pricing complete; model, Fourier method, Monte Carlo method, "
            "and error evidence remain distinct."
        )

    @Slot(int, object)
    def _calibration_completed(self, job_id: int, payload: object) -> None:
        if not self._accept_ui4_result(job_id, "calibration"):
            self._set_status(
                "Heston calibration finished, but its inputs changed; stale result discarded."
            )
            return
        if not isinstance(payload, HestonCalibrationWorkbenchAnalysis):
            self._set_status("UI4 Heston calibration returned an unexpected payload.")
            return
        self._calibration_analysis = payload
        self._apply_calibration_presentation(
            build_heston_calibration_presentation(payload)
        )
        self._set_status(
            "Heston calibration complete; fit, optimizer convergence, and "
            "identifiability evidence remain separate."
        )

    @Slot(int, str)
    def _ui4_worker_failed(self, job_id: int, message: str) -> None:
        if job_id != self._ui4_active_job_id:
            return
        if not self._ui4_active_valid:
            self._set_status(
                "Invalidated quantitative work failed after its inputs changed; "
                "no result was installed."
            )
            return
        self._set_status(f"Quantitative execution failed: {message}")

    @Slot()
    def _ui4_worker_finished(self) -> None:
        self._worker = None
        self._thread = None
        self._ui4_active_job_id = None
        self._ui4_active_kind = ""
        self._ui4_active_valid = True
        self.runningChanged.emit()

    def _begin_ui4_job(self, kind: str) -> int:
        self._ui4_job_sequence += 1
        self._ui4_active_job_id = self._ui4_job_sequence
        self._ui4_active_kind = kind
        self._ui4_active_valid = True
        return self._ui4_job_sequence

    def _accept_ui4_result(self, job_id: int, kind: str) -> bool:
        return (
            job_id == self._ui4_active_job_id
            and kind == self._ui4_active_kind
            and self._ui4_active_valid
        )

    def _start_ui4_worker(
        self,
        worker: _HestonPricingWorker | _HestonCalibrationWorker,
        completed_slot: Callable[[int, object], None],
    ) -> None:
        thread = QThread(self)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.completed.connect(completed_slot)
        worker.failed.connect(self._ui4_worker_failed)
        worker.completed.connect(thread.quit)
        worker.failed.connect(thread.quit)
        worker.completed.connect(worker.deleteLater)
        worker.failed.connect(worker.deleteLater)
        thread.finished.connect(self._ui4_worker_finished)
        thread.finished.connect(thread.deleteLater)
        self._worker = worker
        self._thread = thread
        self.runningChanged.emit()
        thread.start()

    def _clear_heston_presentation(self) -> None:
        self._heston_presentation = None
        self._heston_model.set_items(())
        self._heston_parameters.set_items(())
        self._heston_results.set_items(())
        self._heston_fourier.set_items(())
        self._heston_monte_carlo.set_items(())
        self._heston_inspector.set_items(())
        self.hestonChanged.emit()

    def _apply_heston_presentation(
        self,
        presentation: HestonPricingPresentation,
    ) -> None:
        self._heston_presentation = presentation
        self._heston_model.set_items(presentation.model_rows)
        self._heston_parameters.set_items(presentation.parameter_rows)
        self._heston_results.set_items(presentation.result_rows)
        self._heston_fourier.set_items(presentation.fourier_rows)
        self._heston_monte_carlo.set_items(presentation.monte_carlo_rows)
        self._heston_inspector.set_items(presentation.inspector_rows)
        self.hestonChanged.emit()

    def _clear_calibration_presentation(self) -> None:
        self._calibration_presentation = None
        self._calibration_problem.set_items(())
        self._calibration_truth.set_items(())
        self._calibration_runs.set_items(())
        self._calibration_residuals.set_items(())
        self._calibration_conditioning.set_items(())
        self._calibration_inspector.set_items(())
        self.calibrationChanged.emit()

    def _apply_calibration_presentation(
        self,
        presentation: HestonCalibrationPresentation,
    ) -> None:
        self._calibration_presentation = presentation
        self._calibration_problem.set_items(presentation.problem_rows)
        self._calibration_truth.set_items(presentation.truth_rows)
        self._calibration_runs.set_items(presentation.run_rows)
        self._calibration_residuals.set_items(presentation.residual_rows)
        self._calibration_conditioning.set_items(presentation.conditioning_rows)
        self._calibration_inspector.set_items(presentation.inspector_rows)
        self.calibrationChanged.emit()

    def _apply_m6_market_reference(
        self,
        presentation: M6MarketReferencePresentation,
    ) -> None:
        self._m6_market_summary.set_items(presentation.summary_rows)
        self._m6_market_provenance.set_items(presentation.provenance_rows)
        self._m6_market_starts.set_items(presentation.start_rows)
        self._m6_market_results.set_items(presentation.result_rows)
        self._m6_market_conditioning.set_items(presentation.conditioning_rows)


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
