"""Stochastic-law semantics kept separate from model parameter values."""

from __future__ import annotations

from typing import Protocol

from qf_platform.pricing.state import StateSpace


class StochasticLaw[StateT, ParametersT](Protocol):
    """Structure of a stochastic law without prescribing a process ontology.

    Concrete laws may be diffusions, jump processes, path-dependent models, rough
    processes, or other structures. No universal drift/diffusion interface is assumed.
    Model-specific parameter values remain separate objects supplied by the pricing
    problem.
    """

    @property
    def state_space(self) -> StateSpace[StateT]:
        """Return the state-space semantics governed by this law."""
        ...

    def accepts_parameters(self, parameters: ParametersT, /) -> bool:
        """Return whether this law supports the supplied parameter value object."""
        ...
