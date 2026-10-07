from __future__ import annotations

import base64
import json
import time

import anyio
import httpx2
import pytest

from iikocloudapi import ApiLoginAuth, AppAuth, IikoCloud, Unauthorized
from iikocloudapi._auth import _jwt_expiry
from tests.mock import FakeIiko

pytestmark = pytest.mark.anyio

ORGS = {"correlationId": "c", "organizations": []}


def jwt(exp: float) -> str:
    payload = base64.urlsafe_b64encode(json.dumps({"exp": exp}).encode()).decode().rstrip("=")
    return f"header.{payload}.signature"


def token_requests(fake: FakeIiko) -> list[str]:
    return [r.path for r in fake.requests if r.path.endswith("/access_token")]


async def test_token_is_requested_once_and_reused(fake: FakeIiko) -> None:
    fake.routes["/api/1/organizations"] = ORGS
    async with fake.client() as iiko:
        await iiko.organizations()
        await iiko.organizations()
    assert token_requests(fake) == ["/api/v2/access_token"]
    token_body = fake.requests[0].body
    assert token_body == {"apiKey": "key", "appId": "app", "clientSecret": "secret"}
    assert all(r.headers["Authorization"] == "Bearer token-1" for r in fake.api_requests())


async def test_concurrent_requests_share_one_token_request(fake: FakeIiko) -> None:
    async def slow_token(request: httpx2.Request) -> httpx2.Response:
        await anyio.sleep(0.05)  # let the other requests pile up behind the lock
        return httpx2.Response(200, json={"correlationId": "c", "token": "shared"})

    fake.routes["/api/v2/access_token"] = slow_token
    fake.routes["/api/1/organizations"] = ORGS
    async with fake.client() as iiko, anyio.create_task_group() as tg:
        for _ in range(10):
            tg.start_soon(iiko.organizations)
    assert len(token_requests(fake)) == 1
    assert len(fake.api_requests()) == 10


async def test_expired_token_is_refreshed_once_on_401(fake: FakeIiko) -> None:
    tokens = iter(["old", "new"])
    fake.routes["/api/v2/access_token"] = lambda _: httpx2.Response(200, json={"token": next(tokens)})

    def organizations(request: httpx2.Request) -> httpx2.Response:
        if request.headers["Authorization"] == "Bearer old":
            return httpx2.Response(401, json={"correlationId": "c", "errorDescription": "Token expired"})
        return httpx2.Response(200, json=ORGS)

    fake.routes["/api/1/organizations"] = organizations
    async with fake.client() as iiko:
        await iiko.organizations()
        await iiko.organizations()
    assert len(token_requests(fake)) == 2
    assert [r.headers["Authorization"] for r in fake.api_requests()] == ["Bearer old", "Bearer new", "Bearer new"]


async def test_persistent_401_raises_unauthorized(fake: FakeIiko) -> None:
    fake.routes["/api/1/organizations"] = httpx2.Response(401, json={"correlationId": "c", "errorDescription": "Nope"})
    async with fake.client() as iiko:
        with pytest.raises(Unauthorized, match="Nope"):
            await iiko.organizations()
    assert len(token_requests(fake)) == 2  # one initial, one retry


async def test_failed_token_request_raises(fake: FakeIiko) -> None:
    fake.routes["/api/v2/access_token"] = httpx2.Response(
        401, json={"correlationId": "c", "errorDescription": "Login is not authorized"}
    )
    async with fake.client() as iiko:
        with pytest.raises(Unauthorized, match="Login is not authorized"):
            await iiko.organizations()
    assert fake.api_requests() == []


async def test_jwt_expiry_drives_refresh(fake: FakeIiko, monkeypatch: pytest.MonkeyPatch) -> None:
    now = time.time()
    fake.token = jwt(now + 3600)
    fake.routes["/api/1/organizations"] = ORGS
    auth = AppAuth("key", "app", "secret")
    async with fake.client(auth=auth) as iiko:
        await iiko.organizations()
        monkeypatch.setattr(time, "time", lambda: now + 3600 - 30)  # inside the refresh margin
        await iiko.organizations()
    assert len(token_requests(fake)) == 2


def test_jwt_expiry_parsing() -> None:
    assert _jwt_expiry(jwt(1234)) == 1234
    assert _jwt_expiry("opaque-token") is None
    assert _jwt_expiry("a.!!!.c") is None
    assert _jwt_expiry(jwt(True)) is None  # type: ignore[arg-type]


async def test_invalidate_forces_new_token(fake: FakeIiko) -> None:
    fake.routes["/api/1/organizations"] = ORGS
    auth = AppAuth("key", "app", "secret")
    async with fake.client(auth=auth) as iiko:
        await iiko.organizations()
        assert auth.token == "token-1"
        auth.invalidate()
        await iiko.organizations()
    assert len(token_requests(fake)) == 2


async def test_api_login_auth_is_deprecated_but_works(fake: FakeIiko) -> None:
    fake.routes["/api/1/organizations"] = ORGS
    with pytest.warns(DeprecationWarning, match="AppAuth"):
        auth = ApiLoginAuth("login")
    async with fake.client(auth=auth) as iiko:
        await iiko.organizations()
    assert fake.requests[0].path == "/api/1/access_token"
    assert fake.requests[0].body == {"apiLogin": "login"}


def test_secrets_are_not_in_repr() -> None:
    text = repr(AppAuth("key-value", "app", "s3cr3t"))
    assert "s3cr3t" not in text
    assert "key-value" not in text


def test_sync_clients_are_rejected() -> None:
    with (
        httpx2.Client(transport=httpx2.MockTransport(FakeIiko())) as client,
        pytest.raises(RuntimeError, match="Async"),
    ):
        client.post("https://api-ru.iiko.services/api/1/organizations", auth=AppAuth("k", "a", "s"))


async def test_token_request_inherits_timeout_headers_and_path_prefix(fake: FakeIiko) -> None:
    seen: list[httpx2.Request] = []

    async def record(request: httpx2.Request) -> httpx2.Response:
        seen.append(request)
        return await fake(request)

    fake.routes["/proxy/api/1/organizations"] = ORGS
    http = httpx2.AsyncClient(transport=httpx2.MockTransport(record))
    async with IikoCloud(
        auth=AppAuth("key", "app", "secret"),
        base_url="https://gateway.example/proxy",
        http_client=http,
        headers={"X-Trace": "abc"},
    ) as iiko:
        await iiko.organizations(timeout=7)
    token_request = seen[0]
    assert str(token_request.url) == "https://gateway.example/proxy/api/v2/access_token"
    assert token_request.headers["X-Trace"] == "abc"
    assert token_request.headers["User-Agent"].startswith("iikocloudapi/")
    assert "Timeout" not in token_request.headers
    assert token_request.extensions["timeout"]["read"] == pytest.approx(12)


async def test_invalidated_token_is_refreshed_on_401(fake: FakeIiko) -> None:
    auth = AppAuth("key", "app", "secret")
    tokens = iter(["first", "second"])
    fake.routes["/api/v2/access_token"] = lambda _: httpx2.Response(200, json={"token": next(tokens)})

    def organizations(request: httpx2.Request) -> httpx2.Response:
        if request.headers["Authorization"] == "Bearer first":
            auth.invalidate()  # e.g. another task gave up on the token while this request was in flight
            return httpx2.Response(401, json={"correlationId": "c", "errorDescription": "Expired"})
        return httpx2.Response(200, json=ORGS)

    fake.routes["/api/1/organizations"] = organizations
    async with fake.client(auth=auth) as iiko:
        await iiko.organizations()
    assert [r.headers["Authorization"] for r in fake.api_requests()] == ["Bearer first", "Bearer second"]
