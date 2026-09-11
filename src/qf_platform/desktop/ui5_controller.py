"""Curated PySide6 controller extension for the UI5 validation workspace."""

# pyright: reportRedeclaration=false

from __future__ import annotations

import json

from PySide6.QtCore import Property, QObject, QThread, Signal, Slot

from qf_platform.application.ui5_validation import (
    UI5ValidationAnalysis,
    UI5ValidationRequest,
    make_ui5_reference_validation_request,
    run_ui5_validation,
)
from qf_platform.desktop.models import PresentationRowModel
from qf_platform.desktop.ui4_controller import WorkbenchController as UI4WorkbenchController
from qf_platform.presentation.plotting import PlotData
from qf_platform.presentation.ui5_validation import (
    UI5ValidationPresentation,
    build_ui5_validation_presentation,
)


class _ValidationWorker(QObject):
    """Execute one immutable M7 validation request outside the GUI thread."""

    completed = Signal(object)
    failed = Signal(str)

    def __init__(self, request: UI5ValidationRequest) -> None:
        super().__init__()
        self._request = request

    @Slot()
    def run(self) -> None:
        try:
            analysis = run_ui5_validation(self._request)
        except Exception as exc:  # boundary converts execution failure into UI state
            self.failed.emit(f"{type(exc).__name__}: {exc}")
            return
        self.completed.emit(analysis)


class WorkbenchController(UI4WorkbenchController):
    """Extend UI4 with M7 validation/model-risk evidence without moving math into QML."""

    validationChanged = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._validation_analysis: UI5ValidationAnalysis | None = None
        self._validation_presentation: UI5ValidationPresentation | None = None
        self._validation_summary = PresentationRowModel()
        self._validation_training_metrics = PresentationRowModel()
        self._validation_evaluation_metrics = PresentationRowModel()
        self._validation_residuals = PresentationRowModel()
        self._validation_stability = PresentationRowModel()
        self._validation_risk = PresentationRowModel()
        self._validation_workloads = PresentationRowModel()
        self._validation_inspector = PresentationRowModel()

    @Property(bool, notify=validationChanged)
    def validationAnalysisReady(self) -> bool:  # noqa: N802
        return self._validation_analysis is not None

    @Property(QObject, constant=True)
    def validationSummaryModel(self) -> QObject:  # noqa: N802
        return self._validation_summary

    @Property(QObject, constant=True)
    def validationTrainingMetricModel(self) -> QObject:  # noqa: N802
        return self._validation_training_metrics

    @Property(QObject, constant=True)
    def validationEvaluationMetricModel(self) -> QObject:  # noqa: N802
        return self._validation_evaluation_metrics

    @Property(QObject, constant=True)
    def validationResidualModel(self) -> QObject:  # noqa: N802
        return self._validation_residuals

    @Property(QObject, constant=True)
    def validationStabilityModel(self) -> QObject:  # noqa: N802
        return self._validation_stability

    @Property(QObject, constant=True)
    def validationRiskModel(self) -> QObject:  # noqa: N802
        return self._validation_risk

    @Property(QObject, constant=True)
    def validationWorkloadModel(self) -> QObject:  # noqa: N802
        return self._validation_workloads

    @Property(QObject, constant=True)
    def validationInspectorModel(self) -> QObject:  # noqa: N802
        return self._validation_inspector

    @Property(str, notify=validationChanged)
    def validationResidualPlotJson(self) -> str:  # noqa: N802
        presentation = self._validation_presentation
        return "{}" if presentation is None else _serialize_plot(presentation.residual_plot)

    @Property(str, notify=validationChanged)
    def validationHeldOutErrorPlotJson(self) -> str:  # noqa: N802
        presentation = self._validation_presentation
        return (
            "{}"
            if presentation is None
            else _serialize_plot(presentation.held_out_error_plot)
        )

    @Property(str, notify=validationChanged)
    def validationParameterStabilityPlotJson(self) -> str:  # noqa: N802
        presentation = self._validation_presentation
        return (
            "{}"
            if presentation is None
            else _serialize_plot(presentation.parameter_stability_plot)
        )

    @Property(str, notify=validationChanged)
    def validationReportText(self) -> str:  # noqa: N802
        analysis = self._validation_analysis
        if analysis is None:
            return "Run the M7 validation study to populate the evidence report."
        evidence = analysis.evidence
        return "\n".join(
            (
                "Quant Research Workbench — M7 validation evidence",
                "",
                "Design: same-date cross-sectional SPX holdout; 10 training / 4 evaluation contracts.",
                f"Black-Scholes fitted sigma: {evidence.black_scholes_fit.annualized_volatility:.8f}",
                (
                    "Held-out price RMSE: Black-Scholes "
                    f"{evidence.black_scholes_evaluation_metrics.root_mean_square_error:.6f}; "
                    f"Heston {evidence.heston_evaluation_metrics.root_mean_square_error:.6f}"
                ),
                (
                    "Held-out half-spread standardized RMSE: Black-Scholes "
                    f"{evidence.black_scholes_evaluation_metrics.standardized_root_mean_square_error:.6f}; "
                    f"Heston {evidence.heston_evaluation_metrics.standardized_root_mean_square_error:.6f}"
                ),
                (
                    "Heston training Jacobian: rank "
                    f"{evidence.heston_stability.training_jacobian_rank}; condition "
                    f"{evidence.heston_stability.training_condition_number}"
                ),
                "",
                "Bounded conclusion:",
                evidence.conclusion.statement,
                "",
                "Non-claims: no temporal OOS test; no authoritative Heston hedge comparison; "
                "conditioning is not posterior uncertainty; M8 workload definitions are not runtime benchmarks.",
            )
        )

    @Slot(result=bool)
    def runValidationStudy(self) -> bool:  # noqa: N802
        """Run the deterministic M7 reference study outside the GUI thread."""

        if self.running:
            self._set_status("Quantitative work is already running.")
            return False
        request = make_ui5_reference_validation_request()
        self._clear_validation_presentation()
        worker = _ValidationWorker(request)
        thread = QThread(self)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.completed.connect(self._validation_completed)
        worker.failed.connect(self._validation_failed)
        worker.completed.connect(thread.quit)
        worker.failed.connect(thread.quit)
        worker.completed.connect(worker.deleteLater)
        worker.failed.connect(worker.deleteLater)
        thread.finished.connect(self._validation_worker_finished)
        thread.finished.connect(thread.deleteLater)
        self._worker = worker
        self._thread = thread
        self.runningChanged.emit()
        self._set_status(
            "Running M7 Black-Scholes vs Heston validation outside the GUI thread. "
            "No pseudo progress is reported because the backend exposes none."
        )
        thread.start()
        return True

    @Slot(object)
    def _validation_completed(self, payload: object) -> None:
        if not isinstance(payload, UI5ValidationAnalysis):
            self._set_status("UI5 validation returned an unexpected payload.")
            return
        self._validation_analysis = payload
        self._apply_validation_presentation(build_ui5_validation_presentation(payload))
        self._set_status(
            "M7 validation complete. Training, held-out evaluation, model-risk limits, "
            "and M8 workload structure remain separate evidence."
        )

    @Slot(str)
    def _validation_failed(self, message: str) -> None:
        self._set_status(f"M7 validation execution failed: {message}")

    @Slot()
    def _validation_worker_finished(self) -> None:
        self._worker = None
        self._thread = None
        self.runningChanged.emit()

    def _clear_validation_presentation(self) -> None:
        self._validation_analysis = None
        self._validation_presentation = None
        self._validation_summary.set_items(())
        self._validation_training_metrics.set_items(())
        self._validation_evaluation_metrics.set_items(())
        self._validation_residuals.set_items(())
        self._validation_stability.set_items(())
        self._validation_risk.set_items(())
        self._validation_workloads.set_items(())
        self._validation_inspector.set_items(())
        self.validationChanged.emit()

    def _apply_validation_presentation(
        self,
        presentation: UI5ValidationPresentation,
    ) -> None:
        self._validation_presentation = presentation
        self._validation_summary.set_items(presentation.summary_rows)
        self._validation_training_metrics.set_items(presentation.training_metric_rows)
        self._validation_evaluation_metrics.set_items(presentation.evaluation_metric_rows)
        self._validation_residuals.set_items(presentation.residual_rows)
        self._validation_stability.set_items(presentation.stability_rows)
        self._validation_risk.set_items(presentation.model_risk_rows)
        self._validation_workloads.set_items(presentation.workload_rows)
        self._validation_inspector.set_items(presentation.inspector_rows)
        self.validationChanged.emit()


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
