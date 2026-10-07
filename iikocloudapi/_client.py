"""The :class:`IikoCloud` client."""

from __future__ import annotations

import json
import math
from collections.abc import Mapping
from decimal import Decimal
from types import TracebackType
from typing import TYPE_CHECKING, Any, Protocol, Self

import anyio
import httpx2
from pydantic import TypeAdapter, ValidationError

from iikocloudapi._base import LENIENT_CONTEXT, to_jsonable
from iikocloudapi._errors import (
    CommandFailed,
    CommandTimeout,
    IikoNetworkError,
    ResponseValidationError,
    error_from_response,
)
from iikocloudapi._version import __version__
from iikocloudapi.resources import IikoCloudResources

if TYPE_CHECKING:
    from iikocloudapi.models.general import SuccessCommandStatus

API_RU = "https://api-ru.iiko.services"
"""Russian region API (default)."""
API_EU = "https://api-eu.iiko.services"
"""European region API."""

DEFAULT_TIMEOUT = 15.0
# Extra time the HTTP client waits on top of the server-side ``Timeout`` header.
_TRANSPORT_MARGIN = 5.0
_MAX_POLL_INTERVAL = 5.0


class _HasCorrelationId(Protocol):
    @property
    def correlation_id(self) -> str: ...


class IikoCloud(IikoCloudResources):
    """Async client for the iikoCloud API.

    Every endpoint of the API is available as a method whose attribute path mirrors the endpoint URL
    (``/api/1/order/create`` is ``iiko.order.create(...)``).

    Args:
        auth: Authentication strategy, usually :class:`~iikocloudapi.AppAuth`.
        base_url: API root, :data:`API_RU` (default) or :data:`API_EU`.
        timeout: Default server-side timeout in seconds, sent in the ``Timeout`` header. iikoCloud waits up to this
            long for the restaurant terminal to answer. Each method also accepts ``timeout=`` to override it.
        http_client: Your own ``httpx2.AsyncClient`` (proxies, custom transports...). It is not closed by
            :meth:`aclose`.
        headers: Extra headers sent with every request.

    Example:
        ```python
        async with IikoCloud(auth=AppAuth(api_key=..., app_id=..., client_secret=...)) as iiko:
            organizations = await iiko.organizations()
        ```
    """

    def __init__(
        self,
        auth: httpx2.Auth,
        *,
        base_url: str = API_RU,
        timeout: float = DEFAULT_TIMEOUT,
        http_client: httpx2.AsyncClient | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        super().__init__(self)
        self.auth = auth
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._owns_http_client = http_client is None
        self._http = http_client or httpx2.AsyncClient()
        self._headers = {"User-Agent": f"iikocloudapi/{__version__}", **(headers or {})}
        self._adapters: dict[Any, TypeAdapter[Any]] = {}

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        """Close the underlying HTTP client (unless it was passed in by you)."""
        if self._owns_http_client:
            await self._http.aclose()

    async def request(self, path: str, body: Any = None, *, timeout: float | None = None) -> Any:
        """Call any endpoint, including ones this library does not know about yet.

        Args:
            path: Endpoint path, for example ``"/api/1/organizations"``.
            body: JSON body: plain data, models, ``Decimal``s and datetimes are converted automatically.
            timeout: Server-side timeout in seconds; defaults to the client setting.

        Returns:
            The decoded JSON response (numbers with a fractional part are returned as ``Decimal``), or ``None``
            for an empty response.
        """
        content = None if body is None else _encode(to_jsonable(body))
        response = await self._send(path, content, timeout)
        if not response.content:
            return None
        return json.loads(response.content, parse_float=Decimal)

    async def wait(
        self,
        command: str | _HasCorrelationId,
        *,
        organization_id: str,
        timeout: float = 60.0,
        poll_interval: float = 1.0,
    ) -> SuccessCommandStatus:
        """Wait until an asynchronous command finishes.

        Methods documented as *commands* (order creation, payments, closing...) only start an operation and return
        its ``correlation_id``. This helper polls ``/api/1/commands/status`` with a growing interval.

        Args:
            command: The response of the command or its ``correlation_id``.
            organization_id: Organization the command belongs to.
            timeout: Maximum time to wait, in seconds.
            poll_interval: Initial delay between status checks, in seconds.

        Raises:
            CommandFailed: The command finished with an error.
            CommandTimeout: The command did not finish within ``timeout``.
        """
        from iikocloudapi.models.general import ErrorCommandStatus, SuccessCommandStatus  # noqa: PLC0415

        correlation_id = command if isinstance(command, str) else command.correlation_id
        deadline = anyio.current_time() + timeout
        interval = poll_interval
        while True:
            status = await self.commands.status(organization_id=organization_id, correlation_id=correlation_id)
            if isinstance(status, SuccessCommandStatus):
                return status
            if isinstance(status, ErrorCommandStatus):
                raise CommandFailed(
                    correlation_id, exception=status.exception, error_reason=status.error_reason, status=status
                )
            remaining = deadline - anyio.current_time()
            if remaining <= 0:
                raise CommandTimeout(correlation_id, timeout)
            await anyio.sleep(min(interval, remaining))
            interval = min(interval * 1.5, _MAX_POLL_INTERVAL)

    def _adapter(self, tp: Any) -> TypeAdapter[Any]:
        adapter = self._adapters.get(tp)
        if adapter is None:
            adapter = self._adapters[tp] = TypeAdapter(tp)
        return adapter

    async def _call(
        self,
        path: str,
        request_type: Any,
        data: Any,
        response_type: Any,
        *,
        timeout: float | None,
    ) -> Any:
        content = None
        if request_type is not None:
            if isinstance(data, dict):
                data = {key: value for key, value in data.items() if value is not None}
            adapter = self._adapter(request_type)
            body = adapter.dump_python(adapter.validate_python(data), by_alias=True, exclude_unset=True)
            content = _encode(to_jsonable(body))
        response = await self._send(path, content, timeout)
        if response_type is None:
            return None
        try:
            return self._adapter(response_type).validate_json(response.content, context=LENIENT_CONTEXT)
        except ValidationError as exc:
            msg = f"Unexpected response from {path}: {exc}"
            raise ResponseValidationError(msg, response) from exc

    async def _send(self, path: str, content: bytes | None, timeout: float | None) -> httpx2.Response:
        server_timeout = self.timeout if timeout is None else timeout
        headers = {
            **self._headers,
            "Content-Type": "application/json",
            "Timeout": str(max(1, math.ceil(server_timeout))),
        }
        request = self._http.build_request(
            "POST",
            f"{self.base_url}{path}",
            content=content,
            headers=headers,
            timeout=server_timeout + _TRANSPORT_MARGIN,
        )
        try:
            response = await self._http.send(request, auth=self.auth)
        except httpx2.RequestError as exc:
            raise IikoNetworkError(f"{type(exc).__name__}: {exc}" if str(exc) else type(exc).__name__) from exc
        if response.is_error:
            raise error_from_response(response)
        return response


def _encode(data: Any) -> bytes:
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode()


__all__ = ["API_EU", "API_RU", "DEFAULT_TIMEOUT", "IikoCloud"]
