"""Run every example against a fake iikoCloud that answers with responses synthesised from the specification."""

from __future__ import annotations

import json
from decimal import Decimal
from typing import Any

import httpx2
import pytest
from fastapi.testclient import TestClient

from examples import delivery, menu_sync, quickstart, table_order_cook_first, table_order_pay_first, webhook_receiver
from tests.contract.synth import Synthesizer, operations, spec
from tests.mock import FakeIiko

pytestmark = pytest.mark.anyio

ORG = "3fa85f64-5717-4562-b3fc-2c963f66afa6"


class SpecFake(FakeIiko):
    """Answers every known endpoint with a fully populated response synthesised from the specification."""

    def respond(self, request: httpx2.Request) -> Any:
        if request.url.path not in self.routes:
            op = next((op for op in operations() if op.url == request.url.path), None)
            if op is not None and op.response is not None:
                self.routes[op.url] = Synthesizer(full=True).value(op.response)
        return super().respond(request)


@pytest.fixture
def spec_fake() -> SpecFake:
    return SpecFake(
        routes={
            "/api/1/commands/status": {"state": "Success"},
            "/api/1/payment_types": {
                "correlationId": "c",
                "paymentTypes": [
                    {
                        "id": "pt-external",
                        "paymentTypeKind": "External",
                        "isDeleted": False,
                        "applicableMarketingCampaigns": [],
                        "terminalGroups": [],
                    }
                ],
            },
        }
    )


def sent(fake: FakeIiko, path: str) -> Any:
    return next(r.body for r in fake.requests if r.path == path)


async def test_quickstart(spec_fake: SpecFake, capsys: pytest.CaptureFixture[str]) -> None:
    async with spec_fake.client() as iiko:
        await quickstart.main(iiko)
    assert "online" in capsys.readouterr().out


async def test_table_order_pay_first(spec_fake: SpecFake, capsys: pytest.CaptureFixture[str]) -> None:
    async with spec_fake.client() as iiko:
        await table_order_pay_first.main(
            iiko,
            organization_id=ORG,
            terminal_group_id="tg",
            table_id="table",
            product_id="soup",
            price=Decimal("450.00"),
            acquirer_payment_id="tbank-1",
        )
    order = sent(spec_fake, "/api/1/order/create")["order"]
    assert order["payments"] == [
        {
            "paymentTypeKind": "External",
            "paymentTypeId": "pt-external",
            "sum": 450,
            "isProcessedExternally": True,
            "paymentAdditionalData": {"type": "External", "customData": "tbank-1"},
        }
    ]
    assert "Order #" in capsys.readouterr().out


async def test_table_order_cook_first(spec_fake: SpecFake, capsys: pytest.CaptureFixture[str]) -> None:
    async with spec_fake.client() as iiko:
        await table_order_cook_first.main(
            iiko,
            organization_id=ORG,
            terminal_group_id="tg",
            table_id="table",
            product_id="steak",
            payment_type_id="pt-external",
        )
    paths = [r.path for r in spec_fake.api_requests() if r.path != "/api/1/commands/status"]
    # the synthesised table already has an open order, so dishes are added to it
    assert paths == [
        "/api/1/order/by_table",
        "/api/1/order/add_items",
        "/api/1/order/by_id",
        "/api/1/order/change_payments",
        "/api/1/order/close",
    ]
    assert sent(spec_fake, "/api/1/order/by_table")["statuses"] == ["New", "Bill"]
    assert "paid" in capsys.readouterr().out


async def test_table_order_cook_first_creates_order_on_empty_table(spec_fake: SpecFake) -> None:
    spec_fake.routes["/api/1/order/by_table"] = {"correlationId": "c", "orders": []}
    async with spec_fake.client() as iiko:
        order_id = await table_order_cook_first.add_dishes(
            iiko, organization_id=ORG, terminal_group_id="tg", table_id="table", items=[]
        )
    assert order_id == spec_fake.routes["/api/1/order/create"]["orderInfo"]["id"]


async def test_delivery(spec_fake: SpecFake, capsys: pytest.CaptureFixture[str]) -> None:
    async with spec_fake.client() as iiko:
        await delivery.main(
            iiko, organization_id=ORG, terminal_group_id="tg", product_id="pizza", cash_payment_type_id="cash"
        )
    order = sent(spec_fake, "/api/1/deliveries/create")["order"]
    assert order["deliveryPoint"]["address"]["type"] == "city"
    assert order["payments"] == [{"paymentTypeKind": "Cash", "paymentTypeId": "cash", "sum": 780}]
    assert "Delivery #" in capsys.readouterr().out


async def test_delivery_rejected(spec_fake: SpecFake, capsys: pytest.CaptureFixture[str]) -> None:
    spec_fake.routes["/api/1/commands/status"] = {"state": "Error", "exception": {"message": "Stop list"}}
    async with spec_fake.client() as iiko:
        await delivery.main(
            iiko, organization_id=ORG, terminal_group_id="tg", product_id="pizza", cash_payment_type_id="cash"
        )
    assert "rejected" in capsys.readouterr().out


async def test_menu_sync(spec_fake: SpecFake, capsys: pytest.CaptureFixture[str]) -> None:
    async with spec_fake.client() as iiko:
        await menu_sync.main(iiko, organization_id=ORG)
    assert "Menu " in capsys.readouterr().out


def test_webhook_receiver(capsys: pytest.CaptureFixture[str]) -> None:
    hook = next(h for h in spec().webhooks() if h.name.startswith("TableOrderUpdate"))
    event = Synthesizer(full=True).value({"$ref": f"#/components/schemas/{hook.schema_key}"})
    client = TestClient(webhook_receiver.app)
    body = json.dumps([event, {"eventType": "Teleport"}])
    assert client.post("/iiko/webhooks", content=body).status_code == 401
    response = client.post(
        "/iiko/webhooks", content=body, headers={"Authorization": f"Bearer {webhook_receiver.WEBHOOK_TOKEN}"}
    )
    assert response.status_code == 200
    out = capsys.readouterr().out
    assert "table order" in out
    assert "Teleport" in out


async def test_webhook_registration(spec_fake: SpecFake) -> None:
    async with spec_fake.client() as iiko:
        await webhook_receiver.register(iiko, organization_id=ORG, url="https://example.com/iiko/webhooks")
    settings = sent(spec_fake, "/api/1/webhooks/update_settings")
    assert settings["webHooksUri"] == "https://example.com/iiko/webhooks"
    assert settings["webHooksFilter"]["tableOrderFilter"] == {"orderStatuses": ["Closed"], "errors": True}
