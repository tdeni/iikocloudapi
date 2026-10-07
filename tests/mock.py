"""A fake iikoCloud server for tests (and examples) built on ``httpx2.MockTransport``."""

from __future__ import annotations

import inspect
import json
from dataclasses import dataclass, field
from typing import Any

import httpx2

from iikocloudapi import AppAuth, IikoCloud


@dataclass
class Recorded:
    path: str
    headers: httpx2.Headers
    body: Any


@dataclass
class FakeIiko:
    """Routes ``POST <path>`` to canned responses and records every request.

    ``routes`` values can be a JSON-serialisable body (status 200), an ``httpx2.Response`` or a (possibly async)
    callable that receives the request. ``/api/v2/access_token`` and ``/api/1/access_token`` answer with a token
    unless overridden. Responses are handed out unread and streaming, like a real network transport does.
    """

    routes: dict[str, Any] = field(default_factory=dict)
    requests: list[Recorded] = field(default_factory=list)
    token: str = "token-1"

    async def __call__(self, request: httpx2.Request) -> httpx2.Response:
        body = json.loads(request.content) if request.content else None
        self.requests.append(Recorded(request.url.path, httpx2.Headers(request.headers), body))
        response = self.respond(request)
        if inspect.isawaitable(response):
            response = await response
        return httpx2.Response(
            response.status_code,
            headers=response.headers,
            stream=httpx2.ByteStream(response.read()),
            request=request,
        )

    def respond(self, request: httpx2.Request) -> Any:
        route = self.routes.get(request.url.path)
        if route is None and request.url.path.endswith("/access_token"):
            return httpx2.Response(200, json={"correlationId": "c0", "token": self.token})
        if route is None:
            return httpx2.Response(404, json={"correlationId": "c0", "errorDescription": "Not found"})
        if callable(route):
            return route(request)
        if isinstance(route, httpx2.Response):
            return route
        return httpx2.Response(200, json=route)

    def api_requests(self) -> list[Recorded]:
        return [r for r in self.requests if not r.path.endswith("/access_token")]

    def client(self, **kwargs: Any) -> IikoCloud:
        http = httpx2.AsyncClient(transport=httpx2.MockTransport(self))
        return IikoCloud(auth=kwargs.pop("auth", AppAuth("key", "app", "secret")), http_client=http, **kwargs)
