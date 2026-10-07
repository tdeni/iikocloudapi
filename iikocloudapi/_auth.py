"""Authentication strategies: they obtain an access token and attach it to every request."""

from __future__ import annotations

import base64
import binascii
import json
import time
from collections.abc import AsyncGenerator, Generator
from typing import Any, ClassVar

import anyio
import httpx2
from typing_extensions import deprecated

from iikocloudapi._errors import ResponseValidationError, error_from_response

_UNAUTHORIZED = 401
_NOT_FORWARDED = frozenset({"authorization", "content-length", "content-type", "host", "timeout"})


class IikoAuth(httpx2.Auth):
    """Base class for token-based authentication against iikoCloud.

    The token is requested lazily, cached until shortly before it expires (the JWT ``exp`` claim when available)
    and refreshed once when a request fails with ``401 Unauthorized``. Concurrent requests share a single token
    request.

    Subclasses define :attr:`token_path` and :meth:`token_payload`. Override :meth:`parse_token_response` to
    support another response format, or :meth:`token_request` to obtain tokens from somewhere else entirely
    (for example a token shared between several worker processes).
    """

    token_path: ClassVar[str]
    refresh_margin: ClassVar[float] = 60.0
    """Refresh the token this many seconds before it expires."""
    fallback_lifetime: ClassVar[float] = 15 * 60.0
    """Assumed lifetime of tokens that do not carry an ``exp`` claim."""

    def __init__(self) -> None:
        self._token: str | None = None
        self._expires_at = 0.0
        self._lock = anyio.Lock()

    def token_payload(self) -> dict[str, Any]:
        raise NotImplementedError

    def token_request(self, request: httpx2.Request) -> httpx2.Request:
        """Request that obtains a new token.

        ``request`` is the API request being authenticated: the token request goes to the same host (keeping any
        path prefix in front of ``/api/``) with the same headers and timeout.
        """
        path = request.url.path
        prefix = path[: path.find("/api/")] if "/api/" in path else ""
        headers = {k: v for k, v in request.headers.items() if k.lower() not in _NOT_FORWARDED}
        headers["Content-Type"] = "application/json"
        extensions = {"timeout": request.extensions["timeout"]} if "timeout" in request.extensions else {}
        return httpx2.Request(
            "POST",
            request.url.copy_with(path=prefix + self.token_path, query=None),
            content=json.dumps(self.token_payload()).encode(),
            headers=headers,
            extensions=extensions,
        )

    def parse_token_response(self, response: httpx2.Response) -> str:
        if response.is_error:
            raise error_from_response(response)
        try:
            token = json.loads(response.content)["token"]
        except (ValueError, KeyError, TypeError) as exc:
            msg = "Token response does not contain a token"
            raise ResponseValidationError(msg, response) from exc
        if not isinstance(token, str) or not token:
            msg = "Token response contains an empty token"
            raise ResponseValidationError(msg, response)
        return token

    @property
    def token(self) -> str | None:
        """The current access token, if one has been obtained."""
        return self._token

    def invalidate(self) -> None:
        """Forget the current token; the next request obtains a new one."""
        self._token = None
        self._expires_at = 0.0

    def _expired(self) -> bool:
        return self._token is None or time.time() >= self._expires_at - self.refresh_margin

    def _store(self, response: httpx2.Response) -> str:
        token = self.parse_token_response(response)
        now = time.time()
        lifetime = (_jwt_expiry(token) or 0.0) - now
        if lifetime <= self.refresh_margin * 2:
            lifetime = self.fallback_lifetime
        self._token = token
        self._expires_at = now + lifetime
        return token

    async def async_auth_flow(self, request: httpx2.Request) -> AsyncGenerator[httpx2.Request, httpx2.Response]:
        if self._expired():
            async with self._lock:
                if self._expired():
                    token_response = yield self.token_request(request)
                    await token_response.aread()
                    self._store(token_response)
        token = self._token
        request.headers["Authorization"] = f"Bearer {token}"
        response = yield request
        if response.status_code == _UNAUTHORIZED:
            async with self._lock:
                # Another request may have refreshed the token while this one was in flight.
                if self._token == token or self._expired():
                    token_response = yield self.token_request(request)
                    await token_response.aread()
                    self._store(token_response)
            request.headers["Authorization"] = f"Bearer {self._token}"
            yield request

    def sync_auth_flow(self, request: httpx2.Request) -> Generator[httpx2.Request, httpx2.Response]:
        msg = "iikocloudapi only supports httpx2.AsyncClient"
        raise RuntimeError(msg)
        yield request  # pragma: no cover


class AppAuth(IikoAuth):
    """Authentication of a registered application (``/api/v2/access_token``).

    1. Register at https://public-api.iikoweb.ru/portal and create an application to get ``app_id`` and a one-time
       ``client_secret``.
    2. In iikoWeb, open "Integrations > API Keys" and generate an ``api_key``.

    Args:
        api_key: API key generated in iikoWeb.
        app_id: Application ID from the developer portal.
        client_secret: Application client secret from the developer portal.
    """

    token_path = "/api/v2/access_token"  # noqa: S105

    def __init__(self, api_key: str, app_id: str, client_secret: str) -> None:
        super().__init__()
        self.api_key = api_key
        self.app_id = app_id
        self.client_secret = client_secret

    def token_payload(self) -> dict[str, Any]:
        return {"apiKey": self.api_key, "appId": self.app_id, "clientSecret": self.client_secret}

    def __repr__(self) -> str:
        return f"AppAuth(app_id={self.app_id!r}, api_key='***', client_secret='***')"


@deprecated("ApiLoginAuth uses the deprecated /api/1/access_token endpoint; use AppAuth instead")
class ApiLoginAuth(IikoAuth):
    """Legacy authentication with a single API login (``/api/1/access_token``).

    iikoCloud marks this endpoint as deprecated; prefer :class:`AppAuth`.

    Args:
        api_login: API login created in iikoWeb.
    """

    token_path = "/api/1/access_token"  # noqa: S105

    def __init__(self, api_login: str) -> None:
        super().__init__()
        self.api_login = api_login

    def token_payload(self) -> dict[str, Any]:
        return {"apiLogin": self.api_login}

    def __repr__(self) -> str:
        return "ApiLoginAuth(api_login='***')"


def _jwt_expiry(token: str) -> float | None:
    """The ``exp`` claim of a JWT (without verifying it), or ``None`` for opaque tokens."""
    parts = token.split(".")
    if len(parts) != 3:  # noqa: PLR2004
        return None
    try:
        payload = json.loads(base64.urlsafe_b64decode(parts[1] + "=" * (-len(parts[1]) % 4)))
    except (ValueError, binascii.Error):
        return None
    exp = payload.get("exp") if isinstance(payload, dict) else None
    return float(exp) if isinstance(exp, int | float) and not isinstance(exp, bool) else None


__all__ = ["ApiLoginAuth", "AppAuth", "IikoAuth"]
