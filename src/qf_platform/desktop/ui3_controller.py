"""Curated PySide6 controller extensions for the concrete UI3 workflows."""

# PySide Property decorators are runtime descriptors whose stubs can look like
# redeclarations to strict Pyright when paired with Python property-style methods.
# pyright: reportRedeclaration=false

from __future__ import annotations

import json
from collections.abc import Callable

from PySide6.QtCore import Property, QObject, QThread, Signal, Slot

from qf_platform.application import (
    HedgeWorkbenchAnalysis,
    HedgeWorkbenchDraft,
    HedgeWorkbenchRequest,
    MarketWorkbenchAnalysis,
    canonical_m4_market_workbench,
    compose_black_scholes_study,
    make_hedge_workbench_request,
    run_hedge_workbench,
)
from qf_platform.application.black_scholes_study import BlackScholesStudyDraft
from qf_platform.desktop.models import (
    HedgeFrequencyModel,
    HedgeStepModel,
    MarketObservationModel,
    PresentationRowModel,
)
from qf_platform.desktop.ui2_controller import (
    WorkbenchController as UI2WorkbenchController,
)
from qf_platform.presentation import (
    HedgeWorkbenchPresentation,
    MarketWorkbenchPresentation,
    PlotData,
    build_hedge_workbench_presentation,
    build_market_workbench_presentation,
    hedge_step_detail_rows,
)


class _HedgeWorker(QObject):
    """Execute one immutable UI3 M3 study outside the GUI thread."""

    completed = Signal(object)
    failed = Signal(str)

    def __init__(self, request: HedgeWorkbenchRequest) -> None:
        super().__init__()
        self._request = request

    @Slot()
    def run(self) -> None:
        try:
            analysis = run_hedge_workbench(self._request)
        except Exception as exc:  # boundary converts execution failure into UI state
            self.failed.emit(f"{type(exc).__name__}: {exc}")
            return
        self.completed.emit(analysis)


class _MarketWorker(QObject):
    """Execute the concrete bundled M4 evidence workflow outside the GUI thread."""

    completed = Signal(object)
    failed = Signal(str)

    @Slot()
    def run(self) -> None:
        try:
            analysis = canonical_m4_market_workbench()
        except Exception as exc:  # boundary converts execution failure into UI state
            self.failed.emit(f"{type(exc).__name__}: {exc}")
            return
        self.completed.emit(analysis)


class WorkbenchController(UI2WorkbenchController):
    """Extend UI2 without flattening control and inverse workflows together."""

    hedgeChanged = Signal()
    marketChanged = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._hedge_request: HedgeWorkbenchRequest | None = None
        self._hedge_analysis: HedgeWorkbenchAnalysis | None = None
        self._hedge_presentation: HedgeWorkbenchPresentation | None = None
        self._market_analysis: MarketWorkbenchAnalysis | None = None
        self._market_presentation: MarketWorkbenchPresentation | None = None

        self._hedge_steps = HedgeStepModel()
        self._hedge_frequencies = HedgeFrequencyModel()
        self._hedge_inspector = PresentationRowModel()
        self._hedge_results = PresentationRowModel()
        self._hedge_aggregate = PresentationRowModel()
        self._hedge_provenance = PresentationRowModel()
        self._hedge_selected_step = PresentationRowModel()

        self._market_observations = MarketObservationModel()
        self._market_diagnostics = PresentationRowModel()
        self._market_provenance = PresentationRowModel()
        self._market_inverse = PresentationRowModel()
        self._market_inspector = PresentationRowModel()
        self._market_empirical_provenance = PresentationRowModel()
        self._market_empirical_summary = PresentationRowModel()

        self._hedge_defaults = HedgeWorkbenchDraft()

    @Property(str, constant=True)
    def defaultGeneratingVolatility(self) -> str:  # noqa: N802
        return self._hedge_defaults.generating_volatility

    @Property(str, constant=True)
    def defaultHedgingVolatility(self) -> str:  # noqa: N802
        return self._hedge_defaults.hedging_volatility

    @Property(str, constant=True)
    def defaultRebalanceDayInterval(self) -> str:  # noqa: N802
        return self._hedge_defaults.rebalance_day_interval

    @Property(str, constant=True)
    def defaultHedgeSeed(self) -> str:  # noqa: N802
        return self._hedge_defaults.seed

    @Property(str, constant=True)
    def defaultHedgeReplicateCount(self) -> str:  # noqa: N802
        return self._hedge_defaults.replicate_count

    @Property(str, constant=True)
    def defaultTransactionCostRate(self) -> str:  # noqa: N802
        return self._hedge_defaults.transaction_cost_rate

    @Property(bool, notify=hedgeChanged)
    def hedgeAnalysisReady(self) -> bool:  # noqa: N802
        return self._hedge_analysis is not None

    @Property(bool, notify=marketChanged)
    def marketAnalysisReady(self) -> bool:  # noqa: N802
        return self._market_analysis is not None

    @Property(QObject, constant=True)
    def hedgeStepModel(self) -> QObject:  # noqa: N802
        return self._hedge_steps

    @Property(QObject, constant=True)
    def hedgeFrequencyModel(self) -> QObject:  # noqa: N802
        return self._hedge_frequencies

    @Property(QObject, constant=True)
    def hedgeInspectorModel(self) -> QObject:  # noqa: N802
        return self._hedge_inspector

    @Property(QObject, constant=True)
    def hedgeResultModel(self) -> QObject:  # noqa: N802
        return self._hedge_results

    @Property(QObject, constant=True)
    def hedgeAggregateModel(self) -> QObject:  # noqa: N802
        return self._hedge_aggregate

    @Property(QObject, constant=True)
    def hedgeProvenanceModel(self) -> QObject:  # noqa: N802
        return self._hedge_provenance

    @Property(QObject, constant=True)
    def hedgeSelectedStepModel(self) -> QObject:  # noqa: N802
        return self._hedge_selected_step

    @Property(QObject, constant=True)
    def marketObservationModel(self) -> QObject:  # noqa: N802
        return self._market_observations

    @Property(QObject, constant=True)
    def marketDiagnosticModel(self) -> QObject:  # noqa: N802
        return self._market_diagnostics

    @Property(QObject, constant=True)
    def marketProvenanceModel(self) -> QObject:  # noqa: N802
        return self._market_provenance

    @Property(QObject, constant=True)
    def marketInverseModel(self) -> QObject:  # noqa: N802
        return self._market_inverse

    @Property(QObject, constant=True)
    def marketInspectorModel(self) -> QObject:  # noqa: N802
        return self._market_inspector

    @Property(QObject, constant=True)
    def marketEmpiricalProvenanceModel(self) -> QObject:  # noqa: N802
        return self._market_empirical_provenance

    @Property(QObject, constant=True)
    def marketEmpiricalSummaryModel(self) -> QObject:  # noqa: N802
        return self._market_empirical_summary

    @Property(str, notify=hedgeChanged)
    def hedgeUnderlyingPlotJson(self) -> str:  # noqa: N802
        return self._hedge_plot_json("underlying")

    @Property(str, notify=hedgeChanged)
    def hedgeValuePlotJson(self) -> str:  # noqa: N802
        return self._hedge_plot_json("value")

    @Property(str, notify=hedgeChanged)
    def hedgeDeltaPlotJson(self) -> str:  # noqa: N802
        return self._hedge_plot_json("delta")

    @Property(str, notify=hedgeChanged)
    def hedgeCashPlotJson(self) -> str:  # noqa: N802
        return self._hedge_plot_json("cash")

    @Property(str, notify=hedgeChanged)
    def hedgeFrequencyPlotJson(self) -> str:  # noqa: N802
        return self._hedge_plot_json("frequency")

    @Property(str, notify=hedgeChanged)
    def hedgeReplicatePlotJson(self) -> str:  # noqa: N802
        return self._hedge_plot_json("replicates")

    @Property(str, notify=marketChanged)
    def syntheticSmilePlotJson(self) -> str:  # noqa: N802
        return self._market_plot_json("synthetic_smile")

    @Property(str, notify=marketChanged)
    def syntheticConditioningPlotJson(self) -> str:  # noqa: N802
        return self._market_plot_json("synthetic_conditioning")

    @Property(str, notify=marketChanged)
    def empiricalSmilePlotJson(self) -> str:  # noqa: N802
        return self._market_plot_json("empirical_smile")

    @Property(str, notify=marketChanged)
    def empiricalConditioningPlotJson(self) -> str:  # noqa: N802
        return self._market_plot_json("empirical_conditioning")

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
        result=bool,
    )
    def runHedgeStudy(  # noqa: N802
        self,
        spot: str,
        strike: str,
        valuation_date: str,
        expiry: str,
        rate: str,
        option_right: str,
        generating_volatility: str,
        hedging_volatility: str,
        rebalance_day_interval: str,
        seed: str,
        replicate_count: str,
        transaction_cost_rate: str,
    ) -> bool:
        """Normalize and execute one concrete M3 hedge study on a QThread."""

        if self.running:
            self._set_status("Quantitative work is already running.")
            return False
        try:
            composition = compose_black_scholes_study(
                BlackScholesStudyDraft(
                    spot=spot,
                    strike=strike,
                    valuation_date=valuation_date,
                    expiry=expiry,
                    annualized_volatility=hedging_volatility,
                    continuously_compounded_rate=rate,
                    continuous_dividend_yield="0",
                    option_right=option_right,
                )
            )
            request = make_hedge_workbench_request(
                composition,
                HedgeWorkbenchDraft(
                    generating_volatility=generating_volatility,
                    hedging_volatility=hedging_volatility,
                    rebalance_day_interval=rebalance_day_interval,
                    seed=seed,
                    replicate_count=replicate_count,
                    transaction_cost_rate=transaction_cost_rate,
                ),
            )
        except (TypeError, ValueError) as exc:
            self._clear_hedge_presentation()
            self._set_status(f"Hedge study invalid: {exc}")
            return False

        self._hedge_request = request
        self._hedge_analysis = None
        self._clear_hedge_presentation()
        worker = _HedgeWorker(request)
        self._start_ui3_worker(worker, self._hedge_completed)
        self._set_status(
            "Running model-generated M3 hedge trajectories and paired replicate evidence…"
        )
        return True

    @Slot(result=bool)
    def loadMarketEvidence(self) -> bool:  # noqa: N802
        """Run the bundled M4 synthetic pipeline and load pinned empirical evidence."""

        if self.running:
            self._set_status("Quantitative work is already running.")
            return False
        self._market_analysis = None
        self._clear_market_presentation()
        worker = _MarketWorker()
        self._start_ui3_worker(worker, self._market_completed)
        self._set_status(
            "Running M4 raw-observation normalization and implied-volatility inference…"
        )
        return True

    @Slot(int)
    def selectHedgeStep(self, index: int) -> None:  # noqa: N802
        presentation = self._hedge_presentation
        if presentation is None:
            self._hedge_selected_step.set_items(())
            return
        self._hedge_selected_step.set_items(hedge_step_detail_rows(presentation, index))
        self.hedgeChanged.emit()

    @Slot(int)
    def selectMarketObservation(self, index: int) -> None:  # noqa: N802
        presentation = self._market_presentation
        if presentation is None or not 0 <= index < len(
            presentation.observation_details
        ):
            self._market_provenance.set_items(())
            self._market_inverse.set_items(())
            self._market_inspector.set_items(())
            self.marketChanged.emit()
            return
        detail = presentation.observation_details[index]
        self._market_provenance.set_items(detail.provenance_rows)
        self._market_inverse.set_items(detail.inverse_rows)
        self._market_inspector.set_items(detail.inspector_rows)
        self.marketChanged.emit()

    @Slot(object)
    def _hedge_completed(self, payload: object) -> None:
        request = self._hedge_request
        if not isinstance(payload, HedgeWorkbenchAnalysis) or request is None:
            self._set_status("UI3 hedging returned an unexpected result payload.")
            return
        self._hedge_analysis = payload
        presentation = build_hedge_workbench_presentation(request, payload)
        self._apply_hedge_presentation(presentation)
        self._set_status(
            "Hedge study complete; selected-path and replicate evidence remain distinct."
        )

    @Slot(object)
    def _market_completed(self, payload: object) -> None:
        if not isinstance(payload, MarketWorkbenchAnalysis):
            self._set_status(
                "UI3 market workflow returned an unexpected result payload."
            )
            return
        self._market_analysis = payload
        presentation = build_market_workbench_presentation(payload)
        self._apply_market_presentation(presentation)
        self._set_status(
            "M4 evidence complete; raw, normalized, inferred, and empirical-derived layers remain explicit."
        )

    def _start_ui3_worker(
        self,
        worker: _HedgeWorker | _MarketWorker,
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

    def _clear_hedge_presentation(self) -> None:
        self._hedge_presentation = None
        self._hedge_steps.set_items(())
        self._hedge_frequencies.set_items(())
        self._hedge_inspector.set_items(())
        self._hedge_results.set_items(())
        self._hedge_aggregate.set_items(())
        self._hedge_provenance.set_items(())
        self._hedge_selected_step.set_items(())
        self.hedgeChanged.emit()

    def _apply_hedge_presentation(
        self,
        presentation: HedgeWorkbenchPresentation,
    ) -> None:
        self._hedge_presentation = presentation
        self._hedge_steps.set_items(presentation.step_rows)
        self._hedge_frequencies.set_items(presentation.frequency_rows)
        self._hedge_inspector.set_items(presentation.inspector_rows)
        self._hedge_results.set_items(presentation.result_rows)
        self._hedge_aggregate.set_items(presentation.aggregate_rows)
        self._hedge_provenance.set_items(presentation.provenance_rows)
        self._hedge_selected_step.set_items(hedge_step_detail_rows(presentation, 0))
        self.hedgeChanged.emit()

    def _clear_market_presentation(self) -> None:
        self._market_presentation = None
        self._market_observations.set_items(())
        self._market_diagnostics.set_items(())
        self._market_provenance.set_items(())
        self._market_inverse.set_items(())
        self._market_inspector.set_items(())
        self._market_empirical_provenance.set_items(())
        self._market_empirical_summary.set_items(())
        self.marketChanged.emit()

    def _apply_market_presentation(
        self,
        presentation: MarketWorkbenchPresentation,
    ) -> None:
        self._market_presentation = presentation
        self._market_observations.set_items(
            tuple(detail.table_row for detail in presentation.observation_details)
        )
        self._market_diagnostics.set_items(presentation.diagnostic_rows)
        self._market_empirical_provenance.set_items(
            presentation.empirical_provenance_rows
        )
        self._market_empirical_summary.set_items(presentation.empirical_summary_rows)
        if presentation.observation_details:
            detail = presentation.observation_details[0]
            self._market_provenance.set_items(detail.provenance_rows)
            self._market_inverse.set_items(detail.inverse_rows)
            self._market_inspector.set_items(detail.inspector_rows)
        self.marketChanged.emit()

    def _hedge_plot_json(self, name: str) -> str:
        presentation = self._hedge_presentation
        if presentation is None:
            return "{}"
        plots = {
            "underlying": presentation.underlying_plot,
            "value": presentation.hedge_value_plot,
            "delta": presentation.delta_plot,
            "cash": presentation.cash_plot,
            "frequency": presentation.frequency_plot,
            "replicates": presentation.replicate_error_plot,
        }
        return _serialize_plot(plots[name])

    def _market_plot_json(self, name: str) -> str:
        presentation = self._market_presentation
        if presentation is None:
            return "{}"
        plots = {
            "synthetic_smile": presentation.synthetic_smile_plot,
            "synthetic_conditioning": presentation.synthetic_conditioning_plot,
            "empirical_smile": presentation.empirical_smile_plot,
            "empirical_conditioning": presentation.empirical_conditioning_plot,
        }
        return _serialize_plot(plots[name])


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
