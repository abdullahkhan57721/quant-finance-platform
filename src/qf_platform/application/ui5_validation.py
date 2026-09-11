"""Frontend-neutral UI5 orchestration for merged M7 validation evidence."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime

from qf_platform.inference import HestonCalibrationCoordinates
from qf_platform.market_data import (
    NormalizedOptionObservation,
    ObservationProvenance,
    OptionExerciseStyle,
    OptionSettlementTime,
    RawOptionQuote,
    RawUnderlyingObservation,
    normalize_european_option_midpoint,
)
from qf_platform.pricing import (
    FlatMoneyMarketNumeraire,
    HestonFourierEuropeanOption,
    OptionRight,
    PricingMeasureSemantics,
)
from qf_platform.validation import (
    BlackScholesHestonValidationEvidence,
    BlackScholesHestonValidationProblem,
    CrossSectionalBlackScholesHestonValidation,
    predeclared_every_third_evaluation_partition,
    validate_black_scholes_vs_heston,
)


@dataclass(frozen=True, slots=True)
class UI5ValidationRequest:
    """One concrete M7 validation problem and method for the native Workbench."""

    problem: BlackScholesHestonValidationProblem
    method: CrossSectionalBlackScholesHestonValidation


@dataclass(frozen=True, slots=True)
class UI5WorkloadDefinition:
    """One M7-defined M8 profiling workload; structural evidence, not timing."""

    workload_id: str
    operation: str
    detail: str


@dataclass(frozen=True, slots=True)
class UI5ValidationAnalysis:
    """Completed M7 evidence plus the structural M8 handoff visible to UI5."""

    evidence: BlackScholesHestonValidationEvidence
    workloads: tuple[UI5WorkloadDefinition, ...]


@dataclass(frozen=True, slots=True)
class _ReferencePoint:
    expiry: date
    strike: float
    right: OptionRight
    midpoint: float
    half_spread: float


_VALUATION_DATE = date(2023, 1, 4)
_SPOT = 3853.39
_RATE = 0.045
_Q = 0.017
_REFERENCE_POINTS = (
    _ReferencePoint(date(2023, 2, 3), 3720.0, OptionRight.PUT, 44.25, 0.25),
    _ReferencePoint(date(2023, 2, 3), 3800.0, OptionRight.PUT, 68.5, 1.1),
    _ReferencePoint(date(2023, 2, 3), 3850.0, OptionRight.PUT, 88.25, 0.35),
    _ReferencePoint(date(2023, 2, 3), 3870.0, OptionRight.CALL, 88.4, 0.3),
    _ReferencePoint(date(2023, 2, 3), 3900.0, OptionRight.CALL, 73.75, 1.25),
    _ReferencePoint(date(2023, 2, 3), 3970.0, OptionRight.CALL, 44.15, 0.25),
    _ReferencePoint(date(2023, 2, 3), 4020.0, OptionRight.CALL, 29.05, 0.35),
    _ReferencePoint(date(2023, 4, 28), 3720.0, OptionRight.PUT, 121.8273087015, 0.5),
    _ReferencePoint(date(2023, 4, 28), 3800.0, OptionRight.PUT, 148.977073064, 0.45),
    _ReferencePoint(date(2023, 4, 28), 3900.0, OptionRight.CALL, 177.5873583345, 0.55),
    _ReferencePoint(date(2023, 4, 28), 3950.0, OptionRight.CALL, 151.3361240419, 0.5),
    _ReferencePoint(date(2023, 4, 28), 4075.0, OptionRight.CALL, 94.7811299864, 0.45),
    _ReferencePoint(date(2023, 4, 28), 4110.0, OptionRight.CALL, 82.1294428015, 1.7),
    _ReferencePoint(date(2023, 4, 28), 4240.0, OptionRight.CALL, 44.5720752756, 0.35),
)


def _reference_observations() -> tuple[NormalizedOptionObservation, ...]:
    provenance = ObservationProvenance(
        provider="UI5 M7 deterministic reference",
        source="derived from published M4 evidence; not raw market data",
        market_date=_VALUATION_DATE,
        retrieved_at=datetime(2026, 9, 10, tzinfo=UTC),
        license_notes="derived research fixture only; raw rows are not redistributed",
    )
    underlying = RawUnderlyingObservation(
        underlying_id="SPX",
        value=_SPOT,
        provenance=provenance,
    )
    observations: list[NormalizedOptionObservation] = []
    for point in _REFERENCE_POINTS:
        quote = RawOptionQuote(
            contract_id=(
                f"SPXW-{point.expiry.isoformat()}-{point.right.value}-{point.strike:g}"
            ),
            underlying_id="SPX",
            expiry=point.expiry,
            strike=point.strike,
            right=point.right,
            exercise_style=OptionExerciseStyle.EUROPEAN,
            provenance=provenance,
            bid=point.midpoint - point.half_spread,
            ask=point.midpoint + point.half_spread,
            settlement_time=OptionSettlementTime.PM,
        )
        observations.append(normalize_european_option_midpoint(quote, underlying))
    return tuple(observations)


def _heston_starts() -> tuple[HestonCalibrationCoordinates, ...]:
    vectors = (
        (0.04, 2.0, 0.04, 0.5, -0.7),
        (0.06, 1.0, 0.06, 0.8, -0.4),
        (0.02, 5.0, 0.02, 0.3, -0.85),
    )
    return tuple(
        HestonCalibrationCoordinates.from_vector(
            vector,
            continuous_dividend_yield=_Q,
        )
        for vector in vectors
    )


def make_ui5_reference_validation_request() -> UI5ValidationRequest:
    """Build the deterministic M7 reference study from package-safe derived inputs."""

    observations = _reference_observations()
    training, evaluation = predeclared_every_third_evaluation_partition(observations)
    numeraire = FlatMoneyMarketNumeraire(
        reference_date=_VALUATION_DATE,
        continuously_compounded_rate=_RATE,
    )
    problem = BlackScholesHestonValidationProblem(
        observations=observations,
        training_contract_ids=training,
        evaluation_contract_ids=evaluation,
        numeraire=numeraire,
        pricing_measure=PricingMeasureSemantics(name="Q^N", numeraire=numeraire),
        continuous_dividend_yield=_Q,
        heston_forward_method=HestonFourierEuropeanOption(
            integration_upper_bound=100.0,
            intervals=128,
        ),
    )
    method = CrossSectionalBlackScholesHestonValidation(
        black_scholes_initial_volatility=0.21,
        heston_initial_guesses=_heston_starts(),
        max_function_evaluations=300,
    )
    return UI5ValidationRequest(problem=problem, method=method)


def run_ui5_validation(request: UI5ValidationRequest) -> UI5ValidationAnalysis:
    """Execute authoritative M7 validation without adding UI-owned finance math."""

    evidence = validate_black_scholes_vs_heston(request.problem, request.method)
    computation = evidence.computation
    workloads = (
        UI5WorkloadDefinition(
            "bs_closed_form_single",
            "One Black-Scholes closed-form European-option valuation",
            "M8 must time this separately from model quality evidence.",
        ),
        UI5WorkloadDefinition(
            "heston_fourier_single",
            "One Heston Fourier valuation",
            (
                f"upper={computation.heston_fourier_upper_bound:g}, "
                f"intervals={computation.heston_fourier_intervals}"
            ),
        ),
        UI5WorkloadDefinition(
            "heston_mc_reference",
            "One seeded Heston Monte Carlo valuation",
            "20,000 paths · 252 timesteps · seed 20260910 (M7 handoff definition)",
        ),
        UI5WorkloadDefinition(
            "heston_training_calibration",
            "10-target Heston training calibration",
            (
                f"{computation.heston_training_start_count} starts · function evaluations "
                f"{computation.heston_training_function_evaluations}"
            ),
        ),
        UI5WorkloadDefinition(
            "heston_full_sample_stability_calibration",
            "14-target Heston full-sample stability calibration",
            (
                f"{computation.heston_full_sample_start_count} starts · function evaluations "
                f"{computation.heston_full_sample_function_evaluations}"
            ),
        ),
        UI5WorkloadDefinition(
            "m7_end_to_end_cross_sectional_validation",
            "Complete 10-train / 4-evaluation M7 validation study",
            "Structural workload only; UI5 Phase A does not claim measured runtime.",
        ),
    )
    return UI5ValidationAnalysis(evidence=evidence, workloads=workloads)


__all__ = [
    "UI5ValidationAnalysis",
    "UI5ValidationRequest",
    "UI5WorkloadDefinition",
    "make_ui5_reference_validation_request",
    "run_ui5_validation",
]
