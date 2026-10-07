from __future__ import annotations

import datetime
from decimal import Decimal

import httpx2
import pytest

from iikocloudapi import API_EU, IikoCloud, IikoNetworkError, ResponseValidationError, ServerError
from iikocloudapi.models import CancelCausesResponse, GetOrganizationsRequest, ProductOrderItem
from tests.mock import FakeIiko

pytestmark = pytest.mark.anyio

ORGS = {"correlationId": "c", "organizations": []}


async def test_headers_and_default_timeout(fake: FakeIiko) -> None:
    fake.routes["/api/1/organizations"] = ORGS
    async with fake.client(headers={"X-Trace": "1"}) as iiko:
        await iiko.organizations()
    (request,) = fake.api_requests()
    assert request.headers["Timeout"] == "15"
    assert request.headers["Content-Type"] == "application/json"
    assert request.headers["User-Agent"].startswith("iikocloudapi/")
    assert request.headers["X-Trace"] == "1"


async def test_per_call_timeout_sets_header_and_transport_timeout() -> None:
    seen: list[httpx2.Request] = []

    async def handler(request: httpx2.Request) -> httpx2.Response:
        seen.append(request)
        return await FakeIiko(routes={"/api/1/organizations": ORGS})(request)

    async with IikoCloud(
        auth=FakeIiko().client().auth, http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler))
    ) as iiko:
        await iiko.organizations(timeout=42.5)
    request = seen[-1]
    assert request.headers["Timeout"] == "43"
    assert request.extensions["timeout"]["read"] == pytest.approx(47.5)


async def test_base_url(fake: FakeIiko) -> None:
    seen: list[str] = []

    async def handler(request: httpx2.Request) -> httpx2.Response:
        seen.append(str(request.url))
        return await fake(request)

    fake.routes["/api/1/organizations"] = ORGS
    http = httpx2.AsyncClient(transport=httpx2.MockTransport(handler))
    async with IikoCloud(auth=FakeIiko().client().auth, base_url=API_EU + "/", http_client=http) as iiko:
        await iiko.organizations()
    assert seen[-1] == "https://api-eu.iiko.services/api/1/organizations"


async def test_none_arguments_are_not_sent(fake: FakeIiko) -> None:
    fake.routes["/api/1/organizations"] = ORGS
    async with fake.client() as iiko:
        await iiko.organizations(organization_ids=None, include_disabled=True)
    assert fake.api_requests()[0].body == {"includeDisabled": True}


async def test_nested_arguments_accept_models_and_dicts(fake: FakeIiko) -> None:
    fake.routes["/api/1/order/add_items"] = {"correlationId": "c"}
    async with fake.client() as iiko:
        await iiko.order.add_items(
            organization_id="o",
            order_id="x",
            items=[
                ProductOrderItem(product_id="p1", amount=Decimal(1), price=Decimal("99.90")),
                {"type": "Product", "productId": "p2", "amount": 2, "price": 10},
                {"type": "Product", "product_id": "p3", "amount": "0.5", "price": "1.25"},
            ],
        )
    assert fake.api_requests()[0].body["items"] == [
        {"type": "Product", "productId": "p1", "amount": 1, "price": 99.9},
        {"type": "Product", "productId": "p2", "amount": 2, "price": 10},
        {"type": "Product", "productId": "p3", "amount": 0.5, "price": 1.25},
    ]


async def test_endpoint_without_request_body(fake: FakeIiko) -> None:
    fake.routes["/api/1/tips_types"] = {"correlationId": "c", "tipsTypes": []}
    async with fake.client() as iiko:
        result = await iiko.tips_types()
    assert result.tips_types == []
    assert fake.api_requests()[0].body is None


async def test_endpoint_without_response_body(fake: FakeIiko) -> None:
    fake.routes["/api/1/deliveries/update_tracking_link"] = httpx2.Response(200)
    async with fake.client() as iiko:
        result = await iiko.deliveries.update_tracking_link(
            organization_id="o", order_id="x", tracking_link="https://t"
        )
    assert result is None


async def test_list_response(fake: FakeIiko) -> None:
    fake.routes["/api/finance/v1/account-type/list"] = [{"code": "CASH", "title": "Cash"}]
    async with fake.client() as iiko:
        result = await iiko.finance.account_type.list()
    assert isinstance(result, list)
    assert result[0].code == "CASH"
    assert result[0].model_extra == {}


async def test_raw_request(fake: FakeIiko) -> None:
    fake.routes["/api/1/brand_new"] = {"correlationId": "c", "price": 12.30, "count": 3}
    async with fake.client() as iiko:
        result = await iiko.request(
            "/api/1/brand_new",
            {
                "sum": Decimal("10.50"),
                "when": datetime.datetime(2024, 1, 2, 3, 4, 5, 678000),
                "day": datetime.date(2024, 1, 2),
                "filter": GetOrganizationsRequest(include_disabled=True),
            },
        )
    assert result == {"correlationId": "c", "price": Decimal("12.3"), "count": 3}
    assert fake.api_requests()[0].body == {
        "sum": 10.5,
        "when": "2024-01-02 03:04:05.678",
        "day": "2024-01-02",
        "filter": {"includeDisabled": True},
    }


async def test_network_errors_are_wrapped(fake: FakeIiko) -> None:
    def broken(request: httpx2.Request) -> httpx2.Response:
        raise httpx2.ConnectError("boom", request=request)

    fake.routes["/api/1/organizations"] = broken
    async with fake.client() as iiko:
        with pytest.raises(IikoNetworkError, match="ConnectError: boom") as info:
            await iiko.organizations()
    assert isinstance(info.value.__cause__, httpx2.ConnectError)


async def test_unexpected_response_raises_response_validation_error(fake: FakeIiko) -> None:
    fake.routes["/api/1/cancel_causes"] = {"correlationId": "c", "cancelCauses": "not a list"}
    async with fake.client() as iiko:
        with pytest.raises(ResponseValidationError, match="cancel_causes") as info:
            await iiko.cancel_causes(organization_ids=["o"])
    assert info.value.response.status_code == 200


async def test_error_status_raises(fake: FakeIiko) -> None:
    fake.routes["/api/1/cancel_causes"] = httpx2.Response(500, text="<html>Internal error</html>")
    async with fake.client() as iiko:
        with pytest.raises(ServerError, match="Internal error"):
            await iiko.cancel_causes(organization_ids=["o"])


async def test_response_models_keep_unknown_fields(fake: FakeIiko) -> None:
    fake.routes["/api/1/cancel_causes"] = {
        "correlationId": "c",
        "cancelCauses": [{"id": "1", "name": "Late", "isDeleted": False, "isFancy": True}],
        "newTopLevel": 1,
    }
    async with fake.client() as iiko:
        result = await iiko.cancel_causes(organization_ids=["o"])
    assert isinstance(result, CancelCausesResponse)
    assert result.model_extra == {"newTopLevel": 1}
    assert result.cancel_causes[0].model_extra == {"isFancy": True}


async def test_owned_http_client_is_closed_external_is_not() -> None:
    iiko = IikoCloud(auth=FakeIiko().client().auth)
    await iiko.aclose()
    assert iiko._http.is_closed

    external = httpx2.AsyncClient()
    async with IikoCloud(auth=FakeIiko().client().auth, http_client=external):
        pass
    assert not external.is_closed
    await external.aclose()


async def test_deprecated_endpoint_warns(fake: FakeIiko) -> None:
    fake.routes["/api/1/deliveries/update_order_courier"] = {"correlationId": "c"}
    async with fake.client() as iiko:
        with pytest.warns(DeprecationWarning, match="update_order_courier"):
            await iiko.deliveries.update_order_courier(organization_id="o", order_id="x", employee_id="e")


async def test_raw_request_rejects_nan(fake: FakeIiko) -> None:
    async with fake.client() as iiko:
        with pytest.raises(ValueError, match="JSON compliant"):
            await iiko.request("/api/1/anything", {"sum": float("nan")})
    assert fake.api_requests() == []
