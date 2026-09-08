"""Composition of the mathematical question asked by asset pricing."""

from __future__ import annotations

from dataclasses import dataclass

from qf_platform.pricing.contracts import FinancialContract
from qf_platform.pricing.measures import (
    Numeraire,
    PricingMeasureSemantics,
    validated_numeraire_value,
)
from qf_platform.pricing.models import StochasticLaw
from qf_platform.pricing.state import ModeledState


@dataclass(frozen=True, slots=True)
class PricingProblem[TimeT, StateT, ParametersT]:
    """Immutable statement of what theoretical financial value is being requested.

    ``stochastic_law`` and ``parameters`` are the dynamics supplied under
    ``pricing_measure``. The problem does not own a transformation from physical to
    pricing dynamics, and it does not choose a valuation algorithm.
    """

    current_state: ModeledState[TimeT, StateT]
    stochastic_law: StochasticLaw[StateT, ParametersT]
    parameters: ParametersT
    contract: FinancialContract[TimeT, StateT]
    numeraire: Numeraire[TimeT]
    pricing_measure: PricingMeasureSemantics[TimeT]

    def __post_init__(self) -> None:
        if not self.stochastic_law.state_space.contains(self.current_state.value):
            msg = "current state is incompatible with the stochastic law"
            raise ValueError(msg)
        if not self.stochastic_law.accepts_parameters(self.parameters):
            msg = "parameters are incompatible with the stochastic law"
            raise TypeError(msg)
        if not isinstance(self.pricing_measure, PricingMeasureSemantics):
            msg = "pricing problems require pricing-measure, not physical-measure, semantics"
            raise TypeError(msg)
        if self.pricing_measure.numeraire is not self.numeraire:
            msg = "pricing measure must be associated with the pricing problem numeraire"
            raise ValueError(msg)
        validated_numeraire_value(self.numeraire, self.current_state.time)

    @property
    def valuation_time(self) -> TimeT:
        """Return the time at which the pricing question is conditioned."""

        return self.current_state.time
