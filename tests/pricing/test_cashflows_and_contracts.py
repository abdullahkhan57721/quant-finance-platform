from dataclasses import FrozenInstanceError

import pytest

from qf_platform.pricing import CashFlow, CashFlowStream
from tests.pricing._fixtures import FixedPaymentContract, ScalarPath


def test_cash_flow_and_stream_are_immutable_value_objects() -> None:
    flow = CashFlow(payment_time=1.0, amount=12)
    stream = CashFlowStream((flow,))

    assert flow.amount == 12.0
    assert tuple(stream) == (flow,)
    assert len(stream) == 1

    with pytest.raises(FrozenInstanceError):
        flow.amount = 13.0  # type: ignore[misc]

    with pytest.raises(FrozenInstanceError):
        stream.cash_flows = ()  # type: ignore[misc]


def test_cash_flow_rejects_non_finite_amount() -> None:
    with pytest.raises(ValueError, match="finite"):
        CashFlow(payment_time=1.0, amount=float("nan"))


def test_contract_maps_a_state_path_to_a_cash_flow_stream() -> None:
    contract = FixedPaymentContract(payment_time=2.0, amount=-5.0)
    path = ScalarPath(value=123.0)

    stream = contract.cash_flows(path)

    assert stream == CashFlowStream((CashFlow(payment_time=2.0, amount=-5.0),))
