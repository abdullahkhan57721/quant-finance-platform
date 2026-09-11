"""Measured M8 batch kernel for repeated Heston Fourier European-option prices.

The readable scalar :class:`HestonFourierEuropeanOption` implementation remains the
pricing reference. This helper removes repeated strike-independent characteristic-
function work when several compatible problems share state, parameters, and expiry.
It is deliberately method-specific rather than a generic pricing-backend abstraction.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from math import isfinite, log, pi
from typing import cast

import numpy as np
from numpy.typing import NDArray

from qf_platform.pricing.dates import actual_365_fixed_year_fraction
from qf_platform.pricing.equity import EuropeanOption, OptionRight
from qf_platform.pricing.heston import HestonEquityState, HestonParameters
from qf_platform.pricing.heston_fourier import (
    HestonFourierEuropeanOption,
    heston_characteristic_function,
)
from qf_platform.pricing.measures import validated_numeraire_value
from qf_platform.pricing.numeraire import FlatMoneyMarketNumeraire
from qf_platform.pricing.problem import PricingProblem


class IncompatibleHestonFourierBatch(ValueError):
    """Raised when problems do not share the numerical invariants of one batch."""


def _simpson_weights(intervals: int) -> NDArray[np.float64]:
    weights = np.ones(intervals + 1, dtype=np.float64)
    weights[1:-1:2] = 4.0
    weights[2:-1:2] = 2.0
    return weights


def _validate_common_problem(
    reference: PricingProblem[date, HestonEquityState, HestonParameters],
    candidate: PricingProblem[date, HestonEquityState, HestonParameters],
    method: HestonFourierEuropeanOption,
) -> None:
    if not method.supports(candidate):
        msg = (
            "every batch item must be supported by the configured Heston Fourier method"
        )
        raise IncompatibleHestonFourierBatch(msg)
    if candidate.valuation_time != reference.valuation_time:
        msg = "batch items must share one valuation time"
        raise IncompatibleHestonFourierBatch(msg)
    if candidate.current_state.value != reference.current_state.value:
        msg = "batch items must share spot and instantaneous variance"
        raise IncompatibleHestonFourierBatch(msg)
    if candidate.parameters != reference.parameters:
        msg = "batch items must share one Heston parameter value"
        raise IncompatibleHestonFourierBatch(msg)
    if candidate.numeraire != reference.numeraire:
        msg = "batch items must share one numeraire"
        raise IncompatibleHestonFourierBatch(msg)
    if candidate.pricing_measure != reference.pricing_measure:
        msg = "batch items must share one pricing-measure semantics value"
        raise IncompatibleHestonFourierBatch(msg)


def _expiry_values(
    indexed_problems: list[
        tuple[int, PricingProblem[date, HestonEquityState, HestonParameters]]
    ],
    *,
    method: HestonFourierEuropeanOption,
) -> list[tuple[int, float]]:
    reference = indexed_problems[0][1]
    contract = cast(EuropeanOption, reference.contract)
    year_fraction = actual_365_fixed_year_fraction(
        reference.valuation_time,
        contract.expiry,
    )
    if year_fraction <= 0.0:
        msg = "M8 Heston Fourier batching requires positive time to expiry"
        raise IncompatibleHestonFourierBatch(msg)
    if reference.parameters.volatility_of_variance <= 0.0:
        msg = "M8 Heston Fourier batching requires positive volatility of variance"
        raise IncompatibleHestonFourierBatch(msg)

    spot = reference.current_state.value.spot
    initial_variance = reference.current_state.value.instantaneous_variance
    if spot <= 0.0:
        msg = "M8 Heston Fourier batching requires positive spot"
        raise IncompatibleHestonFourierBatch(msg)
    rate = cast(
        FlatMoneyMarketNumeraire,
        reference.numeraire,
    ).continuously_compounded_rate
    log_spot = log(spot)
    numeraire_now = validated_numeraire_value(
        reference.numeraire,
        reference.valuation_time,
    )
    numeraire_expiry = validated_numeraire_value(reference.numeraire, contract.expiry)
    risk_free_discount = numeraire_now / numeraire_expiry
    dividend_discount = np.exp(
        -reference.parameters.continuous_dividend_yield * year_fraction
    )
    discounted_spot = spot * float(dividend_discount)

    width = (
        method.integration_upper_bound - method.integration_lower_bound
    ) / method.intervals
    frequencies = np.asarray(
        [
            method.integration_lower_bound + index * width
            for index in range(method.intervals + 1)
        ],
        dtype=np.float64,
    )
    complex_frequencies = frequencies.astype(np.complex128)
    phi_minus_i = heston_characteristic_function(
        -1j,
        log_spot=log_spot,
        year_fraction=year_fraction,
        rate=rate,
        parameters=reference.parameters,
        initial_variance=initial_variance,
    )
    if abs(phi_minus_i) == 0.0:
        msg = "Heston first-moment characteristic-function value must be non-zero"
        raise ValueError(msg)

    phi_p1 = np.asarray(
        [
            heston_characteristic_function(
                complex(frequency - 1j),
                log_spot=log_spot,
                year_fraction=year_fraction,
                rate=rate,
                parameters=reference.parameters,
                initial_variance=initial_variance,
            )
            for frequency in complex_frequencies
        ],
        dtype=np.complex128,
    )
    phi_p2 = np.asarray(
        [
            heston_characteristic_function(
                complex(frequency),
                log_spot=log_spot,
                year_fraction=year_fraction,
                rate=rate,
                parameters=reference.parameters,
                initial_variance=initial_variance,
            )
            for frequency in complex_frequencies
        ],
        dtype=np.complex128,
    )

    contracts = [
        cast(EuropeanOption, problem.contract) for _, problem in indexed_problems
    ]
    strikes = np.asarray([item.strike for item in contracts], dtype=np.float64)
    if np.any(strikes <= 0.0):
        msg = "M8 Heston Fourier batching requires positive strikes"
        raise IncompatibleHestonFourierBatch(msg)
    log_strikes = np.log(strikes)
    phases = np.exp(-1j * log_strikes[:, None] * frequencies[None, :])
    denominators = 1j * frequencies
    p1_integrands = np.real(
        phases * phi_p1[None, :] / (denominators[None, :] * phi_minus_i)
    )
    p2_integrands = np.real(phases * phi_p2[None, :] / denominators[None, :])
    weights = _simpson_weights(method.intervals)
    p1 = 0.5 + (width / 3.0) * (p1_integrands @ weights) / pi
    p2 = 0.5 + (width / 3.0) * (p2_integrands @ weights) / pi

    discounted_strikes = strikes * risk_free_discount
    calls = discounted_spot * p1 - discounted_strikes * p2
    puts = discounted_strikes * (1.0 - p2) - discounted_spot * (1.0 - p1)
    values = np.asarray(
        [
            calls[index] if item.right is OptionRight.CALL else puts[index]
            for index, item in enumerate(contracts)
        ],
        dtype=np.float64,
    )
    if not np.all(np.isfinite(values)):
        msg = "batched Heston Fourier present values must be finite"
        raise ValueError(msg)
    return [
        (original_index, float(values[index]))
        for index, (original_index, _problem) in enumerate(indexed_problems)
    ]


def batch_heston_fourier_present_values(
    problems: tuple[PricingProblem[date, HestonEquityState, HestonParameters], ...],
    method: HestonFourierEuropeanOption,
    /,
) -> tuple[float, ...]:
    """Return prices while sharing characteristic-function work within each expiry.

    The helper is stateless. There is no cache to invalidate: every invocation derives
    its numerical arrays from the supplied immutable financial problems.
    """

    if not problems:
        return ()
    reference = problems[0]
    if not method.supports(reference):
        msg = (
            "every batch item must be supported by the configured Heston Fourier method"
        )
        raise IncompatibleHestonFourierBatch(msg)
    for problem in problems[1:]:
        _validate_common_problem(reference, problem, method)

    grouped: dict[
        date,
        list[tuple[int, PricingProblem[date, HestonEquityState, HestonParameters]]],
    ] = defaultdict(list)
    for index, problem in enumerate(problems):
        contract = cast(EuropeanOption, problem.contract)
        grouped[contract.expiry].append((index, problem))

    output = [0.0] * len(problems)
    for indexed_problems in grouped.values():
        for index, value in _expiry_values(indexed_problems, method=method):
            if not isfinite(value):
                msg = "batched Heston Fourier present values must be finite"
                raise ValueError(msg)
            output[index] = value
    return tuple(output)
