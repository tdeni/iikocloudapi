from __future__ import annotations

import httpx2
import pytest

from iikocloudapi import CommandFailed, CommandTimeout
from tests.mock import FakeIiko

pytestmark = pytest.mark.anyio


def statuses(*bodies: dict) -> object:
    queue = list(bodies)

    def handler(request: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(200, json=queue.pop(0) if len(queue) > 1 else queue[0])

    return handler


async def test_wait_until_success(fake: FakeIiko) -> None:
    fake.routes["/api/1/commands/status"] = statuses(
        {"state": "InProgress"}, {"state": "InProgress"}, {"state": "Success"}
    )
    async with fake.client() as iiko:
        status = await iiko.wait("corr", organization_id="org", poll_interval=0.001)
    assert status.state == "Success"
    assert [r.body for r in fake.api_requests()] == [{"organizationId": "org", "correlationId": "corr"}] * 3


async def test_wait_accepts_a_command_response(fake: FakeIiko) -> None:
    fake.routes["/api/1/order/close"] = {"correlationId": "corr-9"}
    fake.routes["/api/1/commands/status"] = {"state": "Success"}
    async with fake.client() as iiko:
        response = await iiko.order.close(organization_id="org", order_id="x")
        await iiko.wait(response, organization_id="org")
    assert fake.api_requests()[-1].body == {"organizationId": "org", "correlationId": "corr-9"}


async def test_wait_raises_command_failed(fake: FakeIiko) -> None:
    fake.routes["/api/1/commands/status"] = {
        "state": "Error",
        "exception": {"code": "PaymentFailed", "message": "Terminal rejected the payment"},
        "errorReason": "TerminalError",
    }
    async with fake.client() as iiko:
        with pytest.raises(CommandFailed) as info:
            await iiko.wait("corr", organization_id="org")
    assert str(info.value) == "Command corr failed: Terminal rejected the payment"
    assert info.value.correlation_id == "corr"
    assert info.value.error_reason == "TerminalError"


async def test_wait_times_out(fake: FakeIiko) -> None:
    fake.routes["/api/1/commands/status"] = {"state": "InProgress"}
    async with fake.client() as iiko:
        with pytest.raises(CommandTimeout) as info:
            await iiko.wait("corr", organization_id="org", timeout=0.05, poll_interval=0.01)
    assert isinstance(info.value, TimeoutError)
    assert len(fake.api_requests()) >= 2
