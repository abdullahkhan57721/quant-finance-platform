from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from qf_platform.pricing import (
    CashFlow,
    CashFlowStream,
    ModeledState,
    PricingMeasureSemantics,
    PricingProblem,
    ValuationResult,
    validated_numeraire_value,
)


@dataclass(frozen=True, slots=True)
class ScalarStateSpace:
    minimum: float = 0.0

    def contains(self, value: float, /) -> bool:
        return value >= self.minimum


@dataclass(frozen=True, slots=True)
class ScalarPath:
    value: float

    def value_at(self, time: float, /) -> float:
        del time
        return self.value


@dataclass(frozen=True, slots=True)
class DeterministicParameters:
    level: float


@dataclass(frozen=True, slots=True)
class DeterministicLaw:
    state_space: ScalarStateSpace

    def accepts_parameters(self, parameters: DeterministicParameters, /) -> bool:
        return parameters.level >= 0.0


@dataclass(frozen=True, slots=True)
class FixedPaymentContract:
    payment_time: float
    amount: float

    def cash_flows(self, path: ScalarPath, /) -> CashFlowStream[float]:
        del path
        return CashFlowStream((CashFlow(self.payment_time, self.amount),))


@dataclass(frozen=True, slots=True)
class LinearNumeraire:
    intercept: float
    slope: float

    def value_at(self, time: float, /) -> float:
        return self.intercept + self.slope * time


@dataclass(frozen=True, slots=True)
class FixedPaymentValuation:
    def supports(
        self,
        problem: PricingProblem[
            float,
            float,
            DeterministicParameters,
            ScalarPath,
        ],
        /,
    ) -> bool:
        return isinstance(problem.contract, FixedPaymentContract)

    def apply(
        self,
        problem: PricingProblem[
            float,
            float,
            DeterministicParameters,
            ScalarPath,
        ],
        /,
    ) -> ValuationResult:
        contract = cast(FixedPaymentContract, problem.contract)
        value_now = validated_numeraire_value(problem.numeraire, problem.valuation_time)
        value_then = validated_numeraire_value(
            problem.numeraire,
            contract.payment_time,
        )
        return ValuationResult(contract.amount * value_now / value_then)


@dataclass(frozen=True, slots=True)
class RejectingValuation:
    applied: bool = False

    def supports(
        self,
        problem: PricingProblem[
            float,
            float,
            DeterministicParameters,
            ScalarPath,
        ],
        /,
    ) -> bool:
        del problem
        return False

    def apply(
        self,
        problem: PricingProblem[
            float,
            float,
            DeterministicParameters,
            ScalarPath,
        ],
        /,
    ) -> ValuationResult:
        del problem
        raise AssertionError("unsupported valuation method must not be applied")


def make_problem() -> PricingProblem[
    float,
    float,
    DeterministicParameters,
    ScalarPath,
]:
    state_space = ScalarStateSpace()
    law = DeterministicLaw(state_space)
    parameters = DeterministicParameters(level=1.0)
    current_state = ModeledState(time=0.0, value=100.0, state_space=state_space)
    contract = FixedPaymentContract(payment_time=1.0, amount=110.0)
    numeraire = LinearNumeraire(intercept=1.0, slope=0.1)
    pricing_measure = PricingMeasureSemantics(name="Q^N", numeraire=numeraire)
    return PricingProblem(
        current_state=current_state,
        stochastic_law=law,
        parameters=parameters,
        contract=contract,
        numeraire=numeraire,
        pricing_measure=pricing_measure,
    )
