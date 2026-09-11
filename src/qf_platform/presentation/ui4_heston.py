"""Renderer-neutral UI4 presentation for Heston pricing and calibration."""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

from qf_platform.application.ui4_heston import (
    HestonCalibrationWorkbenchAnalysis,
    HestonPricingAnalysis,
    HestonPricingRequest,
    M6MarketReference,
    annualized_volatility_from_variance,
)
from qf_platform.presentation.black_scholes import PresentationRow
from qf_platform.presentation.plotting import PlotData, PlotPoint, PlotSeries
from qf_platform.pricing import EuropeanOption, FlatMoneyMarketNumeraire, OptionRight

_PARAMETER_LABELS = ("v0", "kappa", "theta", "xi", "rho")


@dataclass(frozen=True, slots=True)
class HestonPricingPresentation:
    """Concrete renderer-neutral display values for one Heston pricing run."""

    model_rows: tuple[PresentationRow, ...]
    parameter_rows: tuple[PresentationRow, ...]
    result_rows: tuple[PresentationRow, ...]
    fourier_rows: tuple[PresentationRow, ...]
    monte_carlo_rows: tuple[PresentationRow, ...]
    inspector_rows: tuple[PresentationRow, ...]
    method_comparison_plot: PlotData
    fourier_stability_plot: PlotData


@dataclass(frozen=True, slots=True)
class HestonCalibrationPresentation:
    """Concrete renderer-neutral display values for one synthetic M6 calibration run."""

    problem_rows: tuple[PresentationRow, ...]
    truth_rows: tuple[PresentationRow, ...]
    run_rows: tuple[PresentationRow, ...]
    residual_rows: tuple[PresentationRow, ...]
    conditioning_rows: tuple[PresentationRow, ...]
    inspector_rows: tuple[PresentationRow, ...]
    parameter_error_plot: PlotData
    residual_plot: PlotData
    objective_plot: PlotData


@dataclass(frozen=True, slots=True)
class M6MarketReferencePresentation:
    """Display-only values for the committed derived M6 SPX calibration evidence."""

    summary_rows: tuple[PresentationRow, ...]
    provenance_rows: tuple[PresentationRow, ...]
    start_rows: tuple[PresentationRow, ...]
    result_rows: tuple[PresentationRow, ...]
    conditioning_rows: tuple[PresentationRow, ...]
    residual_plot: PlotData
    objective_plot: PlotData


def _fmt(value: float) -> str:
    return f"{value:.10g}"


def _vector_rows(
    values: tuple[float, float, float, float, float],
    *,
    prefix: str = "",
    detail: str = "",
) -> tuple[PresentationRow, ...]:
    return tuple(
        PresentationRow(f"{prefix}{label}", _fmt(value), detail)
        for label, value in zip(_PARAMETER_LABELS, values, strict=True)
    )


def build_heston_pricing_presentation(
    request: HestonPricingRequest,
    analysis: HestonPricingAnalysis,
) -> HestonPricingPresentation:
    """Expose model, method, result, and numerical evidence without flattening them."""

    problem = request.problem
    contract = problem.contract
    numeraire = problem.numeraire
    if not isinstance(contract, EuropeanOption):
        raise TypeError("UI4 Heston presentation requires a EuropeanOption")
    if not isinstance(numeraire, FlatMoneyMarketNumeraire):
        raise TypeError(
            "UI4 Heston presentation requires a flat money-market numeraire"
        )

    state = problem.current_state.value
    parameters = problem.parameters
    right = "Call" if contract.right is OptionRight.CALL else "Put"
    current_volatility = annualized_volatility_from_variance(
        state.instantaneous_variance
    )
    long_run_volatility = sqrt(parameters.long_run_variance)

    model_rows = (
        PresentationRow(
            "Mathematical question",
            "Forward pricing of a European option",
            "The contract/question can remain unchanged while the modeled law changes.",
        ),
        PresentationRow(
            "Black-Scholes reference composition",
            "state S_t · one constant volatility parameter",
            "The existing UI2 workspace uses GBM/Black-Scholes; this row is conceptual comparison, not a second valuation run.",
        ),
        PresentationRow(
            "Selected Heston composition",
            "state (S_t, v_t) · stochastic variance · correlated shocks",
            "Heston changes modeled state/law/parameterization, not the option contract automatically.",
            "Heston selected",
        ),
        PresentationRow(
            "Contract",
            f"European {right} · K={contract.strike:g} · expiry={contract.expiry}",
            "Contract semantics are independent of stochastic-law and valuation-method choices.",
        ),
    )
    parameter_rows = (
        PresentationRow(
            "Current spot S0",
            _fmt(state.spot),
            "Current modeled equity spot.",
        ),
        PresentationRow(
            "Current variance v0",
            _fmt(state.instantaneous_variance),
            f"State-like instantaneous annualized variance; sqrt(v0)={current_volatility:.6g}.",
        ),
        PresentationRow(
            "Mean-reversion speed kappa",
            _fmt(parameters.mean_reversion_speed),
            "Positive speed per model year pulling variance toward theta.",
        ),
        PresentationRow(
            "Long-run variance theta",
            _fmt(parameters.long_run_variance),
            f"Annualized variance level; sqrt(theta)={long_run_volatility:.6g}.",
        ),
        PresentationRow(
            "Volatility of variance xi",
            _fmt(parameters.volatility_of_variance),
            "Variance-process diffusion scale; distinct from volatility itself.",
        ),
        PresentationRow(
            "Correlation rho",
            _fmt(parameters.correlation),
            "Instantaneous spot/variance Brownian-shock correlation in [-1, 1].",
        ),
        PresentationRow(
            "Continuous dividend/carry q",
            _fmt(parameters.continuous_dividend_yield),
            "Finite continuously compounded proportional annualized yield.",
        ),
        PresentationRow(
            "Feller diagnostic",
            _fmt(parameters.feller_discriminant),
            "2*kappa*theta - xi^2. Sufficient strict-positivity diagnostic, not a universal validity constraint.",
            "Satisfied" if parameters.feller_condition_satisfied else "Not satisfied",
        ),
    )

    fourier = analysis.fourier_result
    monte_carlo = analysis.monte_carlo_result
    se_units = analysis.difference_in_monte_carlo_standard_errors
    se_text = (
        "not defined (zero sampling SE)"
        if se_units is None
        else f"{se_units:.4g} MC SE"
    )
    result_rows = (
        PresentationRow(
            "Fourier price",
            _fmt(fourier.present_value),
            "Characteristic-function valuation with explicit finite quadrature configuration.",
        ),
        PresentationRow(
            "Monte Carlo price",
            _fmt(monte_carlo.present_value),
            "Independent seeded simulation under the same Heston pricing problem.",
        ),
        PresentationRow(
            "Absolute method difference",
            _fmt(analysis.absolute_method_difference),
            f"Difference is {se_text}; it is evidence to interpret, not a generic UI error.",
        ),
        PresentationRow(
            "Fourier within MC 95% interval",
            "Yes" if analysis.fourier_inside_monte_carlo_95 else "No",
            "This addresses MC sampling uncertainty only; it does not eliminate time-discretization or Fourier integration error.",
        ),
        PresentationRow(
            "No path display",
            "Not available from merged M5 valuation results",
            "UI4 does not synthesize decorative S_t/v_t trajectories that the backend did not record.",
            "Intentional",
        ),
    )
    fourier_rows = (
        PresentationRow(
            "Valuation method",
            "Heston Fourier / characteristic function",
            "Numerical method is separate from the Heston stochastic law.",
        ),
        PresentationRow(
            "Integration interval",
            f"[{fourier.integration_lower_bound:g}, {fourier.integration_upper_bound:g}]",
            "Finite frequency-domain truncation belongs to this method.",
        ),
        PresentationRow(
            "Composite Simpson intervals",
            str(fourier.intervals),
            "Even quadrature resolution; changing it changes numerical approximation, not Heston parameters.",
        ),
        PresentationRow(
            "Characteristic-function evaluations",
            str(fourier.characteristic_function_evaluations),
            "Structural work count retained by the M5 result.",
        ),
    )
    mc_lower, mc_upper = monte_carlo.confidence_interval_95
    proposal_rate = monte_carlo.negative_variance_proposals / (
        monte_carlo.paths * monte_carlo.time_steps
    )
    monte_carlo_rows = (
        PresentationRow(
            "Valuation method",
            "Heston Monte Carlo",
            "Seeded independent M5 method; not the Heston model itself.",
        ),
        PresentationRow(
            "Sampling uncertainty",
            f"SE={monte_carlo.standard_error:.6g}; 95%=[{mc_lower:.6g}, {mc_upper:.6g}]",
            "Normal-approximation interval for sampling error only.",
        ),
        PresentationRow(
            "Simulation configuration",
            f"{monte_carlo.paths} paths · {monte_carlo.time_steps} timesteps · seed {monte_carlo.seed}",
            "Explicit local RNG ownership; equal seeds are not a cross-backend stream identity contract.",
        ),
        PresentationRow(
            "Variance scheme",
            monte_carlo.variance_scheme,
            "Full-truncation Euler when xi>0; exact deterministic-variance boundary where applicable.",
        ),
        PresentationRow(
            "Negative variance proposals",
            f"{monte_carlo.negative_variance_proposals} ({proposal_rate:.3%} of transitions)",
            "Boundary-pressure/discretization evidence, not a financial-model error count.",
        ),
    )
    inspector_rows = (
        PresentationRow(
            "State",
            f"S={state.spot:g}; v={state.instantaneous_variance:g}",
            "Heston current state contains spot plus instantaneous variance.",
        ),
        PresentationRow(
            "Stochastic law",
            "Risk-neutral Heston stochastic volatility",
            "dS=(r-q)Sdt+sqrt(v)S dW_S; dv=kappa(theta-v)dt+xi sqrt(v)dW_v with correlation rho.",
        ),
        PresentationRow(
            "Parameters",
            (
                f"kappa={parameters.mean_reversion_speed:g}; "
                f"theta={parameters.long_run_variance:g}; "
                f"xi={parameters.volatility_of_variance:g}; "
                f"rho={parameters.correlation:g}; "
                f"q={parameters.continuous_dividend_yield:g}"
            ),
            "Immutable M5 Heston structural parameter value; v0 remains current state.",
        ),
        PresentationRow(
            "Pricing measure",
            problem.pricing_measure.name,
            "Numeraire-associated pricing semantics; not a physical-world forecast measure.",
        ),
        PresentationRow(
            "Contract",
            f"European {right}; K={contract.strike:g}; expiry={contract.expiry}",
            "Same contract may be priced under Black-Scholes or Heston.",
        ),
        PresentationRow(
            "Pricing problem",
            f"PV at {problem.valuation_time}; r={numeraire.continuously_compounded_rate:g}",
            "State + law + parameters + contract + numeraire + pricing measure.",
        ),
        PresentationRow(
            "Valuation methods",
            "Heston Fourier AND Heston Monte Carlo",
            "Independent numerical methods over the same pricing problem.",
        ),
        PresentationRow(
            "Numerical assumptions",
            f"Fourier intervals={fourier.intervals}; MC paths={monte_carlo.paths}, steps={monte_carlo.time_steps}",
            "Sampling, time-discretization, and quadrature/truncation errors remain distinct.",
        ),
    )

    method_comparison_plot = PlotData(
        title="Heston independent-method comparison",
        x_label="Method index: 0 Fourier · 1 Monte Carlo",
        y_label="Present value",
        series=(
            PlotSeries(
                key="fourier",
                label="Fourier",
                points=(PlotPoint(x=0.0, y=fourier.present_value),),
            ),
            PlotSeries(
                key="monte_carlo",
                label="Monte Carlo (95% sampling interval)",
                points=(
                    PlotPoint(
                        x=1.0,
                        y=monte_carlo.present_value,
                        lower=mc_lower,
                        upper=mc_upper,
                    ),
                ),
            ),
        ),
    )
    fourier_stability_plot = PlotData(
        title="Fourier resolution stability on the same pricing problem",
        x_label="Simpson intervals",
        y_label="Present value",
        series=(
            PlotSeries(
                key="fourier_stability",
                label="Fourier",
                points=tuple(
                    PlotPoint(x=float(item.intervals), y=item.present_value)
                    for item in analysis.fourier_stability
                ),
            ),
        ),
    )
    return HestonPricingPresentation(
        model_rows=model_rows,
        parameter_rows=parameter_rows,
        result_rows=result_rows,
        fourier_rows=fourier_rows,
        monte_carlo_rows=monte_carlo_rows,
        inspector_rows=inspector_rows,
        method_comparison_plot=method_comparison_plot,
        fourier_stability_plot=fourier_stability_plot,
    )


def build_heston_calibration_presentation(
    analysis: HestonCalibrationWorkbenchAnalysis,
) -> HestonCalibrationPresentation:
    """Prepare truth-recovery or rank-deficiency evidence from completed M6 results."""

    problem = analysis.problem
    truth = analysis.truth
    primary = analysis.runs[0].result
    mode_name = (
        "Synthetic truth recovery"
        if analysis.mode == "recovery"
        else "Thin non-identifiability experiment"
    )
    problem_rows = (
        PresentationRow(
            "Calibration workspace",
            mode_name,
            "Calibration is a separate inverse question rather than a model-panel action.",
        ),
        PresentationRow(
            "Targets",
            f"{len(problem.targets)} synthetic option prices",
            "Targets are model-generated under known Heston truth and never masquerade as observations.",
        ),
        PresentationRow(
            "Target space",
            "Option price",
            "Merged M6 does not implement implied-volatility-space Heston calibration.",
            "M6 authority",
        ),
        PresentationRow(
            "Weighting",
            problem.weighting.value,
            "Residual scaling belongs to HestonCalibrationProblem, not the optimizer.",
        ),
        PresentationRow(
            "Unknown coordinates",
            "v0, kappa, theta, xi, rho",
            "Direct financial coordinates; spot, rate, and q remain fixed.",
        ),
        PresentationRow(
            "Forward operator",
            f"HestonFourierEuropeanOption · {problem.forward_method.intervals} intervals",
            "M5 forward pricing is called inside the M6 residual map.",
        ),
        PresentationRow(
            "Financial bounds",
            (
                "v0 [0.005,0.15] · kappa [0.2,6] · theta [0.005,0.15] · "
                "xi [0.1,1.5] · rho [-0.95,-0.1]"
            ),
            "Concrete UI4 truth-recovery domain matches M6 deterministic evidence; Feller is not enforced.",
        ),
    )
    truth_rows = (
        PresentationRow(
            "Truth v0",
            _fmt(truth.initial_variance),
            "Known only because this is a synthetic validation experiment.",
        ),
        PresentationRow("Truth kappa", _fmt(truth.parameters.mean_reversion_speed)),
        PresentationRow("Truth theta", _fmt(truth.parameters.long_run_variance)),
        PresentationRow("Truth xi", _fmt(truth.parameters.volatility_of_variance)),
        PresentationRow("Truth rho", _fmt(truth.parameters.correlation)),
    )

    run_rows: list[PresentationRow] = []
    for run in analysis.runs:
        estimate = run.result.estimate.as_vector()
        run_rows.append(
            PresentationRow(
                run.label,
                " · ".join(
                    f"{label}={value:.6g}"
                    for label, value in zip(_PARAMETER_LABELS, estimate, strict=True)
                ),
                (
                    f"objective={run.result.objective_value:.6g}; "
                    f"nfev={run.result.function_evaluations}; "
                    f"rank={run.result.conditioning.jacobian_rank}/5"
                ),
                (
                    "Rank deficient"
                    if run.result.conditioning.rank_deficient
                    else "Full local rank"
                ),
            )
        )

    residual_rows = tuple(
        PresentationRow(
            item.target.label or f"Target {index + 1}",
            f"target={item.target.target_price:.8g}; model={item.model_price:.8g}",
            (
                f"model-target={item.residual:.4g}; "
                f"standardized={item.standardized_residual:.4g}"
            ),
        )
        for index, item in enumerate(primary.residuals)
    )
    condition_number = primary.conditioning.condition_number
    conditioning_rows = (
        PresentationRow(
            "Objective value",
            _fmt(primary.objective_value),
            "Sum of squared problem-standardized price residuals.",
        ),
        PresentationRow(
            "Optimizer",
            primary.optimizer_name,
            f"status={primary.termination_status}; {primary.termination_message}",
            "Converged",
        ),
        PresentationRow(
            "Function / Jacobian evaluations",
            f"{primary.function_evaluations} / {primary.jacobian_evaluations}",
            "Numerical search work retained by HestonCalibrationResult.",
        ),
        PresentationRow(
            "Local Jacobian rank",
            f"{primary.conditioning.jacobian_rank} / {primary.conditioning.parameter_count}",
            "Rank deficiency means local first-order identification is incomplete.",
            (
                "Rank deficient"
                if primary.conditioning.rank_deficient
                else "Full local rank"
            ),
        ),
        PresentationRow(
            "Domain-scaled condition number",
            "not finite / not reported"
            if condition_number is None
            else _fmt(condition_number),
            "Reported only for full five-parameter local rank; local conditioning is not posterior uncertainty.",
        ),
        PresentationRow(
            "Interpretation",
            (
                "Tiny fit loss can coexist with materially different parameters."
                if analysis.mode == "thin"
                else "Truth recovery checks the complete forward-map → residual → optimizer → immutable-result path."
            ),
            "Good price fit != stable parameter estimate != identified structural parameter.",
            "Identifiability evidence",
        ),
    )
    inspector_rows = (
        PresentationRow(
            "Observed / target quantities",
            f"{len(problem.targets)} synthetic option-price targets",
            "Synthetic target source is explicit; no market provenance is claimed.",
        ),
        PresentationRow(
            "Unknowns",
            "v0, kappa, theta, xi, rho",
            "Five direct financial coordinates; no hidden transformed optimizer coordinates.",
        ),
        PresentationRow(
            "Forward operator",
            "M5 Heston Fourier pricing",
            "Maps one coordinate set and each European contract to model price.",
        ),
        PresentationRow(
            "Objective",
            "sum_i ((model_price_i - target_price_i) / scale_i)^2",
            "Price-space M6 objective.",
        ),
        PresentationRow(
            "Weights",
            problem.weighting.value,
            "Uniform scale=1 for the synthetic experiment.",
        ),
        PresentationRow(
            "Constraints",
            "HestonCalibrationBounds",
            "Financial admissible domain; Feller condition remains diagnostic rather than enforced.",
        ),
        PresentationRow(
            "Inverse method / optimizer",
            primary.optimizer_name,
            "Bound-constrained trust-region least squares in direct financial coordinates.",
        ),
        PresentationRow(
            "Result",
            (
                f"objective={primary.objective_value:.6g}; "
                f"max |std residual|={primary.max_absolute_standardized_residual:.6g}"
            ),
            "Immutable HestonCalibrationResult, not mutable optimizer state.",
        ),
        PresentationRow(
            "Conditioning / identifiability",
            f"rank={primary.conditioning.jacobian_rank}/5; condition={condition_number}",
            "Local domain-scaled residual-Jacobian evidence; not proof of global identification.",
        ),
        PresentationRow(
            "Progress stream",
            "Not exposed by merged M6",
            "UI4 shows busy/completed state only and does not manufacture optimizer progress.",
            "Intentional",
        ),
    )

    widths = problem.bounds.widths
    truth_vector = truth.as_vector()
    parameter_series = tuple(
        PlotSeries(
            key=f"run_{run_index}",
            label=run.label,
            points=tuple(
                PlotPoint(
                    x=float(parameter_index),
                    y=(estimate - truth_value) / width,
                )
                for parameter_index, (estimate, truth_value, width) in enumerate(
                    zip(
                        run.result.estimate.as_vector(),
                        truth_vector,
                        widths,
                        strict=True,
                    )
                )
            ),
        )
        for run_index, run in enumerate(analysis.runs)
    )
    parameter_error_plot = PlotData(
        title="Recovered-parameter error scaled by financial-domain width",
        x_label="Parameter index: 0 v0 · 1 kappa · 2 theta · 3 xi · 4 rho",
        y_label="(estimate - truth) / bound width",
        series=parameter_series,
    )
    residual_plot = PlotData(
        title="Primary-start price residuals",
        x_label="Target index",
        y_label="Model price - target price",
        series=(
            PlotSeries(
                key="residual",
                label="Residual",
                points=tuple(
                    PlotPoint(x=float(index), y=item.residual)
                    for index, item in enumerate(primary.residuals)
                ),
            ),
        ),
    )
    objective_plot = PlotData(
        title="Multiple-start calibration objective",
        x_label="Start index",
        y_label="Sum squared standardized residuals",
        series=(
            PlotSeries(
                key="objective",
                label="Objective",
                points=tuple(
                    PlotPoint(x=float(index), y=run.result.objective_value)
                    for index, run in enumerate(analysis.runs)
                ),
            ),
        ),
    )
    return HestonCalibrationPresentation(
        problem_rows=problem_rows,
        truth_rows=truth_rows,
        run_rows=tuple(run_rows),
        residual_rows=residual_rows,
        conditioning_rows=conditioning_rows,
        inspector_rows=inspector_rows,
        parameter_error_plot=parameter_error_plot,
        residual_plot=residual_plot,
        objective_plot=objective_plot,
    )


def build_m6_market_reference_presentation(
    reference: M6MarketReference,
) -> M6MarketReferencePresentation:
    """Render the committed M6 derived SPX evidence without inventing raw observations."""

    summary_rows = (
        PresentationRow(
            "Market snapshot",
            (
                f"{reference.underlying} · {reference.quote_date} · "
                f"spot {reference.observed_spot:g}"
            ),
            (
                f"{reference.target_count} pinned OTM-side contracts across "
                f"{', '.join(reference.expiries)}."
            ),
        ),
        PresentationRow(
            "Calibration target space",
            "Option price",
            "Derived M6 reference; not an implied-volatility-space calibration.",
        ),
        PresentationRow(
            "Weighting",
            reference.weighting,
            "Observed bid/ask half-spread scales price residuals in the raw replay workflow.",
        ),
        PresentationRow(
            "Fixed market inputs",
            (
                f"r={reference.continuously_compounded_rate:g}; "
                f"q={reference.continuous_dividend_yield:g}; ACT/365F"
            ),
            "Risk-free accumulation and carry are fixed rather than inferred.",
        ),
        PresentationRow(
            "Forward method",
            (
                f"Heston Fourier · upper={reference.fourier_upper_bound:g} · "
                f"intervals={reference.fourier_intervals}"
            ),
            "The calibration problem owns its configured M5 forward valuation method.",
        ),
    )
    provenance_rows = (
        PresentationRow(
            "Committed derived evidence",
            reference.source_reference,
            "Package mirror is checked against this repository artifact; the repository artifact remains authoritative.",
        ),
        PresentationRow(
            "Pinned public source",
            (
                f"{reference.source_repository}@{reference.source_commit[:12]} · "
                f"{reference.source_path}"
            ),
            "Raw artifact replay is performed by scripts/m6_heston_calibration.py.",
        ),
        PresentationRow(
            "Pinned Git blob",
            reference.source_git_blob_sha1,
            "Raw rows are not redistributed by UI4.",
        ),
        PresentationRow(
            "License / redistribution note",
            reference.license_note,
            "UI4 presents derived/model evidence only.",
        ),
    )
    start_rows = tuple(
        PresentationRow(
            f"Start {index + 1}",
            "init "
            + ", ".join(
                f"{label}={value:.5g}"
                for label, value in zip(
                    _PARAMETER_LABELS,
                    start.initial_guess,
                    strict=True,
                )
            ),
            (
                "estimate "
                + ", ".join(
                    f"{label}={value:.6g}"
                    for label, value in zip(
                        _PARAMETER_LABELS,
                        start.estimate,
                        strict=True,
                    )
                )
                + (
                    f"; objective={start.objective_value:.8g}; "
                    f"nfev={start.function_evaluations}"
                )
            ),
            "Converged reference run",
        )
        for index, start in enumerate(reference.starts)
    )
    result_rows = (
        *_vector_rows(
            reference.best_estimate,
            prefix="Best ",
            detail="Best recorded M6 real-market financial coordinate estimate.",
        ),
        PresentationRow(
            "Objective",
            _fmt(reference.best_objective_value),
            "Half-spread-standardized sum-squared price residual.",
        ),
        PresentationRow(
            "Max |standardized residual|",
            _fmt(reference.max_absolute_standardized_residual),
            "Largest residual after observed half-spread scaling.",
        ),
        PresentationRow(
            "Optimizer termination",
            f"status={reference.termination_status}; {reference.termination_message}",
            "Optimizer convergence is evidence about numerical search, not model validity.",
            "Converged",
        ),
        PresentationRow(
            "Feller diagnostic",
            f"discriminant={reference.feller_discriminant:.8g}",
            "Not enforced as a calibration constraint.",
            "Satisfied" if reference.feller_condition_satisfied else "Not satisfied",
        ),
    )
    conditioning_rows = (
        PresentationRow(
            "Local Jacobian rank",
            f"{reference.jacobian_rank} / 5",
            "Full local first-order rank for this sample.",
            "Full local rank",
        ),
        PresentationRow(
            "Domain-scaled condition number",
            _fmt(reference.condition_number),
            "Nontrivial conditioning remains despite tight multi-start optimizer clustering.",
        ),
        PresentationRow(
            "Domain-scaled singular values",
            ", ".join(f"{item:.6g}" for item in reference.singular_values),
            "Local residual-Jacobian spectrum; not a posterior distribution.",
        ),
        PresentationRow(
            "Scientific interpretation",
            "Stable optimizer convergence + good fit != identified/valid structural model",
            "M7 owns comparative Black-Scholes-vs-Heston model-risk conclusions.",
            "Do not over-interpret",
        ),
    )
    residual_plot = PlotData(
        title="M6 SPX standardized residuals in pinned contract order",
        x_label="Pinned contract index",
        y_label="Price residual / observed half-spread",
        series=(
            PlotSeries(
                key="standardized_residual",
                label="Standardized residual",
                points=tuple(
                    PlotPoint(x=float(index), y=value)
                    for index, value in enumerate(reference.standardized_residuals)
                ),
            ),
        ),
    )
    objective_plot = PlotData(
        title="M6 SPX multiple-start objective",
        x_label="Start index",
        y_label="Sum squared standardized residuals",
        series=(
            PlotSeries(
                key="objective",
                label="Objective",
                points=tuple(
                    PlotPoint(x=float(index), y=start.objective_value)
                    for index, start in enumerate(reference.starts)
                ),
            ),
        ),
    )
    return M6MarketReferencePresentation(
        summary_rows=summary_rows,
        provenance_rows=provenance_rows,
        start_rows=start_rows,
        result_rows=result_rows,
        conditioning_rows=conditioning_rows,
        residual_plot=residual_plot,
        objective_plot=objective_plot,
    )


__all__ = [
    "HestonCalibrationPresentation",
    "HestonPricingPresentation",
    "M6MarketReferencePresentation",
    "build_heston_calibration_presentation",
    "build_heston_pricing_presentation",
    "build_m6_market_reference_presentation",
]
