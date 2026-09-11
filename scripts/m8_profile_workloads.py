#!/usr/bin/env python3
"""Profile and benchmark the representative M8 workloads frozen by M7.

This is a research/performance evidence entry point, not a production finance API. It
uses the deterministic M7 SPX fixture so runs require no network or raw-market artifact.
Wall-clock measurements are environment-dependent and must be interpreted together with
structural work counts and cProfile evidence.
"""

from __future__ import annotations

import argparse
import cProfile
import json
import os
import platform
import pstats
import sys
from collections.abc import Callable
from dataclasses import asdict
from datetime import UTC, date, datetime
from pathlib import Path
from statistics import median, pstdev
from time import perf_counter
from typing import Any, TypedDict, cast

import numpy as np
import scipy

from qf_platform.inference import (
    HestonCalibrationCoordinates,
    HestonCalibrationProblem,
    HestonCalibrationWeighting,
    HestonPriceCalibrationTarget,
    ScipyLeastSquaresHestonCalibration,
    calibrate_heston,
)
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
    BlackScholesClosedForm,
    BlackScholesLaw,
    BlackScholesParameters,
    EquityState,
    FlatMoneyMarketNumeraire,
    HestonEquityState,
    HestonFourierEuropeanOption,
    HestonLaw,
    HestonMonteCarloEuropeanOption,
    ModeledState,
    OptionRight,
    PricingMeasureSemantics,
    PricingProblem,
    evaluate,
)
from qf_platform.validation import (
    BlackScholesHestonValidationProblem,
    CrossSectionalBlackScholesHestonValidation,
    predeclared_every_third_evaluation_partition,
    validate_black_scholes_vs_heston,
)

_FIXTURE_PATH = (
    Path(__file__).parents[1]
    / "tests"
    / "fixtures"
    / "m7_spx_validation_observations.json"
)
_M7_TRAINING_HESTON = (
    0.044250145053,
    3.496771753215,
    0.064364713285,
    0.595565465797,
    -0.813169002873,
)
_M7_BLACK_SCHOLES_VOLATILITY = 0.208906978911
_M8_MC_PATHS = 20_000
_M8_MC_STEPS = 252
_M8_MC_SEED = 20_260_910


class _Point(TypedDict):
    expiry: str
    strike: float
    right: str
    midpoint: float
    half_spread: float


class _Fixture(TypedDict):
    fixture_kind: str
    valuation_date: str
    underlying: str
    spot: float
    continuously_compounded_rate: float
    continuous_dividend_yield: float
    points: list[_Point]


class _BenchmarkResult(TypedDict):
    repetitions: int
    invocations_per_sample: int
    warmup_samples: int
    samples_seconds_per_invocation: list[float]
    median_seconds_per_invocation: float
    minimum_seconds_per_invocation: float
    maximum_seconds_per_invocation: float
    population_stddev_seconds_per_invocation: float
    output: dict[str, object]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--profile-top", type=int, default=15)
    return parser.parse_args()


def _fixture() -> _Fixture:
    return cast(_Fixture, json.loads(_FIXTURE_PATH.read_text(encoding="utf-8")))


def _observations() -> tuple[NormalizedOptionObservation, ...]:
    fixture = _fixture()
    valuation_date = date.fromisoformat(fixture["valuation_date"])
    provenance = ObservationProvenance(
        provider="M8 deterministic profile fixture",
        source="derived from the published M4/M7 evidence; not raw market data",
        market_date=valuation_date,
        retrieved_at=datetime(2026, 9, 11, tzinfo=UTC),
        license_notes="derived performance fixture only",
    )
    underlying = RawUnderlyingObservation(
        underlying_id=fixture["underlying"],
        value=fixture["spot"],
        provenance=provenance,
    )
    observations: list[NormalizedOptionObservation] = []
    for point in fixture["points"]:
        expiry = date.fromisoformat(point["expiry"])
        right = OptionRight(point["right"])
        midpoint = point["midpoint"]
        half_spread = point["half_spread"]
        quote = RawOptionQuote(
            contract_id=(
                f"SPXW-{expiry.isoformat()}-{right.value}-{point['strike']:g}"
            ),
            underlying_id=fixture["underlying"],
            expiry=expiry,
            strike=point["strike"],
            right=right,
            exercise_style=OptionExerciseStyle.EUROPEAN,
            provenance=provenance,
            bid=midpoint - half_spread,
            ask=midpoint + half_spread,
            settlement_time=OptionSettlementTime.PM,
        )
        observations.append(normalize_european_option_midpoint(quote, underlying))
    return tuple(observations)


def _coordinates(
    values: tuple[float, float, float, float, float],
    *,
    q: float,
) -> HestonCalibrationCoordinates:
    return HestonCalibrationCoordinates.from_vector(
        values,
        continuous_dividend_yield=q,
    )


def _starts(q: float) -> tuple[HestonCalibrationCoordinates, ...]:
    vectors = (
        (0.04, 2.0, 0.04, 0.5, -0.7),
        (0.06, 1.0, 0.06, 0.8, -0.4),
        (0.02, 5.0, 0.02, 0.3, -0.85),
    )
    return tuple(_coordinates(vector, q=q) for vector in vectors)


def _validation_problem() -> BlackScholesHestonValidationProblem:
    fixture = _fixture()
    observations = _observations()
    valuation_date = date.fromisoformat(fixture["valuation_date"])
    numeraire = FlatMoneyMarketNumeraire(
        reference_date=valuation_date,
        continuously_compounded_rate=fixture["continuously_compounded_rate"],
    )
    training, evaluation = predeclared_every_third_evaluation_partition(observations)
    return BlackScholesHestonValidationProblem(
        observations=observations,
        training_contract_ids=training,
        evaluation_contract_ids=evaluation,
        numeraire=numeraire,
        pricing_measure=PricingMeasureSemantics(name="Q^N", numeraire=numeraire),
        continuous_dividend_yield=fixture["continuous_dividend_yield"],
        heston_forward_method=HestonFourierEuropeanOption(
            integration_upper_bound=100.0,
            intervals=256,
        ),
    )


def _calibration_problem(
    validation_problem: BlackScholesHestonValidationProblem,
    observations: tuple[NormalizedOptionObservation, ...],
) -> HestonCalibrationProblem:
    targets = tuple(
        HestonPriceCalibrationTarget.from_normalized_observation(observation)
        for observation in observations
    )
    return HestonCalibrationProblem(
        valuation_date=validation_problem.valuation_date,
        spot=validation_problem.spot,
        targets=targets,
        numeraire=validation_problem.numeraire,
        pricing_measure=validation_problem.pricing_measure,
        continuous_dividend_yield=validation_problem.continuous_dividend_yield,
        bounds=validation_problem.heston_bounds,
        weighting=HestonCalibrationWeighting.BID_ASK_HALF_SPREAD,
        forward_method=validation_problem.heston_forward_method,
    )


def _one_contract(validation_problem: BlackScholesHestonValidationProblem):
    observation = validation_problem.evaluation_observations[0]
    return HestonPriceCalibrationTarget.from_normalized_observation(
        observation
    ).contract


def _black_scholes_problem(
    validation_problem: BlackScholesHestonValidationProblem,
) -> PricingProblem[date, EquityState, BlackScholesParameters]:
    law = BlackScholesLaw()
    return PricingProblem(
        current_state=ModeledState(
            time=validation_problem.valuation_date,
            value=EquityState(validation_problem.spot),
            state_space=law.state_space,
        ),
        stochastic_law=law,
        parameters=BlackScholesParameters(
            annualized_volatility=_M7_BLACK_SCHOLES_VOLATILITY,
            continuous_dividend_yield=validation_problem.continuous_dividend_yield,
        ),
        contract=_one_contract(validation_problem),
        numeraire=validation_problem.numeraire,
        pricing_measure=validation_problem.pricing_measure,
    )


def _heston_problem(
    validation_problem: BlackScholesHestonValidationProblem,
) -> PricingProblem[date, HestonEquityState, Any]:
    coordinates = _coordinates(
        _M7_TRAINING_HESTON,
        q=validation_problem.continuous_dividend_yield,
    )
    law = HestonLaw()
    return PricingProblem(
        current_state=ModeledState(
            time=validation_problem.valuation_date,
            value=HestonEquityState(
                spot=validation_problem.spot,
                instantaneous_variance=coordinates.initial_variance,
            ),
            state_space=law.state_space,
        ),
        stochastic_law=law,
        parameters=coordinates.parameters,
        contract=_one_contract(validation_problem),
        numeraire=validation_problem.numeraire,
        pricing_measure=validation_problem.pricing_measure,
    )


def _run_black_scholes(
    problem: PricingProblem[date, EquityState, BlackScholesParameters],
) -> dict[str, object]:
    result = evaluate(problem, BlackScholesClosedForm())
    return {"present_value": result.present_value}


def _run_heston_fourier(
    problem: PricingProblem[date, HestonEquityState, Any],
) -> dict[str, object]:
    result = evaluate(
        problem,
        HestonFourierEuropeanOption(integration_upper_bound=100.0, intervals=256),
    )
    return {
        "present_value": result.present_value,
        "characteristic_function_evaluations": (
            result.characteristic_function_evaluations
        ),
        "intervals": result.intervals,
    }


def _run_heston_mc(
    problem: PricingProblem[date, HestonEquityState, Any],
) -> dict[str, object]:
    result = evaluate(
        problem,
        HestonMonteCarloEuropeanOption(
            paths=_M8_MC_PATHS,
            time_steps=_M8_MC_STEPS,
            seed=_M8_MC_SEED,
        ),
    )
    return {
        "present_value": result.present_value,
        "standard_error": result.standard_error,
        "negative_variance_proposals": result.negative_variance_proposals,
        "paths": result.paths,
        "time_steps": result.time_steps,
        "path_step_transitions": result.paths * result.time_steps,
        "normal_draws": 2 * result.paths * result.time_steps,
        "seed": result.seed,
    }


def _run_calibration(
    problem: HestonCalibrationProblem,
    starts: tuple[HestonCalibrationCoordinates, ...],
) -> dict[str, object]:
    outputs: list[dict[str, object]] = []
    for initial_guess in starts:
        result = calibrate_heston(
            problem,
            ScipyLeastSquaresHestonCalibration(initial_guess=initial_guess),
        )
        outputs.append(
            {
                "estimate": list(result.estimate.as_vector()),
                "objective_value": result.objective_value,
                "function_evaluations": result.function_evaluations,
                "jacobian_evaluations": result.jacobian_evaluations,
                "jacobian_rank": result.conditioning.jacobian_rank,
            }
        )
    return {
        "target_count": len(problem.targets),
        "start_count": len(starts),
        "starts": outputs,
        "total_reported_function_evaluations": sum(
            int(item["function_evaluations"]) for item in outputs
        ),
        "total_reported_jacobian_evaluations": sum(
            int(item["jacobian_evaluations"]) for item in outputs
        ),
    }


def _run_validation(
    problem: BlackScholesHestonValidationProblem,
    starts: tuple[HestonCalibrationCoordinates, ...],
) -> dict[str, object]:
    evidence = validate_black_scholes_vs_heston(
        problem,
        CrossSectionalBlackScholesHestonValidation(
            black_scholes_initial_volatility=0.21,
            heston_initial_guesses=starts,
        ),
    )
    return {
        "black_scholes_fit": asdict(evidence.black_scholes_fit),
        "heston_training_objective": (
            evidence.selected_heston_training_result.objective_value
        ),
        "heston_evaluation_rmse": (
            evidence.heston_evaluation_metrics.root_mean_square_error
        ),
        "black_scholes_evaluation_rmse": (
            evidence.black_scholes_evaluation_metrics.root_mean_square_error
        ),
        "structural_computation_evidence": asdict(evidence.computation),
    }


def _benchmark(
    run: Callable[[], dict[str, object]],
    *,
    repetitions: int,
    invocations_per_sample: int,
    warmup_samples: int = 1,
) -> _BenchmarkResult:
    if repetitions < 1 or invocations_per_sample < 1 or warmup_samples < 0:
        msg = "benchmark repetition/invocation counts must be positive"
        raise ValueError(msg)

    output: dict[str, object] = {}
    for _ in range(warmup_samples):
        for _ in range(invocations_per_sample):
            output = run()

    samples: list[float] = []
    for _ in range(repetitions):
        started = perf_counter()
        for _ in range(invocations_per_sample):
            output = run()
        elapsed = perf_counter() - started
        samples.append(elapsed / invocations_per_sample)

    return {
        "repetitions": repetitions,
        "invocations_per_sample": invocations_per_sample,
        "warmup_samples": warmup_samples,
        "samples_seconds_per_invocation": samples,
        "median_seconds_per_invocation": median(samples),
        "minimum_seconds_per_invocation": min(samples),
        "maximum_seconds_per_invocation": max(samples),
        "population_stddev_seconds_per_invocation": (
            pstdev(samples) if len(samples) > 1 else 0.0
        ),
        "output": output,
    }


def _profile(
    run: Callable[[], dict[str, object]],
    *,
    top: int,
) -> list[dict[str, object]]:
    profiler = cProfile.Profile()
    profiler.runcall(run)
    stats = pstats.Stats(profiler)
    ranked = sorted(stats.stats.items(), key=lambda item: item[1][3], reverse=True)
    entries: list[dict[str, object]] = []
    for (filename, line, function), values in ranked[:top]:
        primitive_calls, total_calls, self_time, cumulative_time, _callers = values
        entries.append(
            {
                "file": filename,
                "line": line,
                "function": function,
                "primitive_calls": primitive_calls,
                "total_calls": total_calls,
                "self_seconds": self_time,
                "cumulative_seconds": cumulative_time,
            }
        )
    return entries


def _environment() -> dict[str, object]:
    return {
        "git_sha": os.environ.get("GITHUB_SHA", "unknown"),
        "github_run_id": os.environ.get("GITHUB_RUN_ID"),
        "runner_name": os.environ.get("RUNNER_NAME"),
        "runner_os": os.environ.get("RUNNER_OS"),
        "runner_arch": os.environ.get("RUNNER_ARCH"),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "logical_cpu_count": os.cpu_count(),
        "python": sys.version,
        "numpy": np.__version__,
        "scipy": scipy.__version__,
    }


def derive_profile(*, repetitions: int, profile_top: int) -> dict[str, object]:
    validation_problem = _validation_problem()
    bs_problem = _black_scholes_problem(validation_problem)
    heston_problem = _heston_problem(validation_problem)
    starts = _starts(validation_problem.continuous_dividend_yield)
    training_calibration = _calibration_problem(
        validation_problem,
        validation_problem.training_observations,
    )
    full_calibration = _calibration_problem(
        validation_problem,
        validation_problem.observations,
    )

    workloads: dict[str, tuple[Callable[[], dict[str, object]], int]] = {
        "bs_closed_form_single": (
            lambda: _run_black_scholes(bs_problem),
            1000,
        ),
        "heston_fourier_single": (
            lambda: _run_heston_fourier(heston_problem),
            20,
        ),
        "heston_mc_reference": (
            lambda: _run_heston_mc(heston_problem),
            1,
        ),
        "heston_training_calibration": (
            lambda: _run_calibration(training_calibration, starts),
            1,
        ),
        "heston_full_sample_stability_calibration": (
            lambda: _run_calibration(full_calibration, starts),
            1,
        ),
        "m7_end_to_end_cross_sectional_validation": (
            lambda: _run_validation(validation_problem, starts),
            1,
        ),
    }

    benchmark_payload: dict[str, object] = {}
    for name, (run, invocations) in workloads.items():
        benchmark_payload[name] = _benchmark(
            run,
            repetitions=repetitions,
            invocations_per_sample=invocations,
        )

    profile_payload = {
        name: _profile(workloads[name][0], top=profile_top)
        for name in (
            "heston_fourier_single",
            "heston_mc_reference",
            "heston_training_calibration",
            "heston_full_sample_stability_calibration",
            "m7_end_to_end_cross_sectional_validation",
        )
    }

    return {
        "evidence_kind": "M8 representative-workload profile and timing evidence",
        "interpretation": (
            "Wall-clock values are environment-dependent research evidence, not CI "
            "thresholds. Structural counts and cProfile call attribution are retained "
            "to distinguish algorithmic/Python overhead from orchestration."
        ),
        "environment": _environment(),
        "methodology": {
            "warmup_samples": 1,
            "timing_repetitions": repetitions,
            "summary": "median with min/max/population-standard-deviation",
            "profiling": "one cProfile execution per nontrivial workload",
            "timer": "time.perf_counter",
        },
        "workloads": benchmark_payload,
        "profiles": profile_payload,
    }


def main() -> None:
    args = _parse_args()
    if args.repetitions < 1:
        msg = "--repetitions must be positive"
        raise ValueError(msg)
    if args.profile_top < 1:
        msg = "--profile-top must be positive"
        raise ValueError(msg)
    payload = derive_profile(
        repetitions=args.repetitions,
        profile_top=args.profile_top,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
