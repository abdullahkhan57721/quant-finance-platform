from __future__ import annotations

from dataclasses import replace

import pytest

from qf_platform.application import (
    canonical_black_scholes_draft,
    compose_black_scholes_study,
)
from qf_platform.pricing import EuropeanOption, OptionRight


def test_canonical_study_normalizes_to_the_merged_m1_problem() -> None:
    composition = compose_black_scholes_study(canonical_black_scholes_draft())
    problem = composition.problem

    assert problem.current_state.value.spot == 100.0
    assert isinstance(problem.contract, EuropeanOption)
    assert problem.contract.strike == 100.0
    assert problem.contract.right is OptionRight.CALL
    assert problem.parameters.annualized_volatility == 0.20
    assert problem.parameters.continuous_dividend_yield == 0.0
    assert composition.method_supported


def test_transient_invalid_text_never_becomes_financial_state() -> None:
    draft = replace(canonical_black_scholes_draft(), annualized_volatility="twenty")

    with pytest.raises(ValueError, match="annualized volatility must be a number"):
        compose_black_scholes_study(draft)


def test_expired_contract_is_structurally_composable_but_method_unsupported() -> None:
    draft = replace(canonical_black_scholes_draft(), expiry="2025-12-31")
    composition = compose_black_scholes_study(draft)

    assert not composition.method_supported


def test_guided_and_advanced_language_share_one_normalization_path() -> None:
    guided = canonical_black_scholes_draft()
    advanced = replace(
        guided,
        valuation_date="2026-01-01",
        continuously_compounded_rate="0.050",
        continuous_dividend_yield="0.000",
    )

    guided_problem = compose_black_scholes_study(guided).problem
    advanced_problem = compose_black_scholes_study(advanced).problem

    assert guided_problem == advanced_problem
