from dataclasses import FrozenInstanceError

import pytest

from qf_platform.pricing import (
    ModeledState,
    PhysicalMeasureSemantics,
    PricingMeasureSemantics,
    validated_numeraire_value,
)
from tests.pricing._fixtures import (
    DeterministicLaw,
    DeterministicParameters,
    LinearNumeraire,
    ScalarStateSpace,
)


def test_modeled_state_is_separate_from_law_and_parameters() -> None:
    state_space = ScalarStateSpace()
    state = ModeledState(time=0.0, value=2.0, state_space=state_space)
    law = DeterministicLaw(state_space=state_space)
    parameters = DeterministicParameters(level=3.0)

    assert state.value == 2.0
    assert law.state_space is state_space
    assert law.accepts_parameters(parameters)
    assert not hasattr(law, "drift")
    assert not hasattr(law, "diffusion")

    with pytest.raises(FrozenInstanceError):
        state.value = 4.0  # type: ignore[misc]


def test_modeled_state_rejects_values_outside_its_state_space() -> None:
    with pytest.raises(ValueError, match="outside"):
        ModeledState(time=0.0, value=-1.0, state_space=ScalarStateSpace())


def test_physical_and_pricing_measure_semantics_are_distinct() -> None:
    numeraire = LinearNumeraire(intercept=1.0, slope=0.0)
    physical = PhysicalMeasureSemantics()
    pricing = PricingMeasureSemantics(name="Q^N", numeraire=numeraire)

    assert physical.name == "P"
    assert pricing.name == "Q^N"
    assert pricing.numeraire is numeraire
    assert type(physical) is not type(pricing)


def test_numeraire_values_are_checked_at_each_supported_access() -> None:
    positive = LinearNumeraire(intercept=1.0, slope=0.1)
    zero_later = LinearNumeraire(intercept=1.0, slope=-1.0)

    assert validated_numeraire_value(positive, 2.0) == pytest.approx(1.2)

    with pytest.raises(ValueError, match="positive and finite"):
        validated_numeraire_value(zero_later, 1.0)

    invalid = LinearNumeraire(intercept=float("inf"), slope=0.0)
    with pytest.raises(ValueError, match="positive and finite"):
        validated_numeraire_value(invalid, 0.0)
