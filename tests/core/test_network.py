"""End-to-end over a real socket: catches behaviour that in-memory transports hide (e.g. unread streaming bodies)."""

from __future__ import annotations

import json
import threading
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from iikocloudapi import AppAuth, BadRequest, IikoCloud, Unauthorized

pytestmark = pytest.mark.anyio


class Handler(BaseHTTPRequestHandler):
    tokens_issued = 0

    def do_POST(self) -> None:
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"null")
        if self.path == "/api/v2/access_token":
            if body["apiKey"] != "good":
                self.reply(401, {"correlationId": "c", "errorDescription": "Unknown API key"})
                return
            Handler.tokens_issued += 1
            self.reply(200, {"correlationId": "c", "token": f"token-{Handler.tokens_issued}"})
        elif self.headers.get("Authorization") != f"Bearer token-{Handler.tokens_issued}":
            self.reply(401, {"correlationId": "c", "errorDescription": "Bad token"})
        elif self.path == "/api/1/organizations":
            self.reply(
                200, {"correlationId": "c", "organizations": [{"responseType": "Simple", "id": "1", "name": "A"}]}
            )
        else:
            self.reply(400, {"correlationId": "c2", "errorDescription": "Unsupported", "error": "BAD"})

    def reply(self, status: int, body: object) -> None:
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        pass


@pytest.fixture
def server_url() -> Iterator[str]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()
    server.server_close()


async def test_authenticated_request(server_url: str) -> None:
    async with IikoCloud(auth=AppAuth("good", "app", "secret"), base_url=server_url) as iiko:
        result = await iiko.organizations()
        assert result.organizations[0].id == "1"
        with pytest.raises(BadRequest, match="Unsupported"):
            await iiko.cancel_causes(organization_ids=["1"])


async def test_token_errors(server_url: str) -> None:
    async with IikoCloud(auth=AppAuth("bad", "app", "secret"), base_url=server_url) as iiko:
        with pytest.raises(Unauthorized, match="Unknown API key"):
            await iiko.organizations()
