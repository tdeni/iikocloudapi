"""Exceptions raised by iikocloudapi."""

from __future__ import annotations

import json
from typing import Any

import httpx2


class IikoError(Exception):
    """Base class for every error raised by iikocloudapi."""


class IikoNetworkError(IikoError):
    """The request did not reach iikoCloud or the response was not received (connection error, timeout...)."""


class IikoApiError(IikoError):
    """iikoCloud answered with an HTTP error status.

    Attributes:
        status_code: HTTP status code.
        description: Human-readable error description from the response body.
        error: Short error code, if provided (``errorDescription``/``error`` in iikoTransport API responses).
        correlation_id: Operation ID of the failed request, if provided.
        details: Additional error details returned by the newer APIs (inventory, finance, ...).
        response: The raw ``httpx2.Response``.
    """

    status_code: int

    def __init__(
        self,
        response: httpx2.Response,
        *,
        description: str,
        error: str | None = None,
        correlation_id: str | None = None,
        details: Any = None,
    ) -> None:
        self.response = response
        self.status_code = response.status_code
        self.description = description
        self.error = error
        self.correlation_id = correlation_id
        self.details = details
        super().__init__(str(self))

    def __str__(self) -> str:
        text = f"{self.status_code} {self.error or self.response.reason_phrase}: {self.description}"
        if self.correlation_id:
            text += f" (correlationId={self.correlation_id})"
        return text


class BadRequest(IikoApiError):  # noqa: N818
    """400: the request is invalid."""


class Unauthorized(IikoApiError):  # noqa: N818
    """401: credentials are invalid or the token has expired."""


class Forbidden(IikoApiError):  # noqa: N818
    """403: the API login has no access to the requested resource."""


class NotFound(IikoApiError):  # noqa: N818
    """404: the requested entity does not exist."""


class RequestTimeout(IikoApiError):  # noqa: N818
    """408: iikoCloud did not get an answer from the terminal in time (see the ``Timeout`` header)."""


class Conflict(IikoApiError):  # noqa: N818
    """409: the request conflicts with the current state of the entity."""


class Gone(IikoApiError):  # noqa: N818
    """410: the entity is no longer available (for example, an expired ``correlationId``)."""


class UnprocessableEntity(IikoApiError):  # noqa: N818
    """422: the request is well-formed but semantically invalid."""


class TooManyRequests(IikoApiError):  # noqa: N818
    """429: rate limit exceeded.

    Attributes:
        retry_after: Seconds to wait before retrying, if the server sent a ``Retry-After`` header.
    """

    @property
    def retry_after(self) -> float | None:
        value = self.response.headers.get("Retry-After")
        try:
            return float(value) if value is not None else None
        except ValueError:
            return None


class ServerError(IikoApiError):
    """5xx: an error on the iikoCloud side."""


class ResponseValidationError(IikoError):
    """The response body does not match the model this library expects.

    The original ``pydantic.ValidationError`` is available as ``__cause__``.
    """

    def __init__(self, message: str, response: httpx2.Response) -> None:
        super().__init__(message)
        self.response = response


class CommandFailed(IikoError):  # noqa: N818
    """An asynchronous command (see :meth:`IikoCloud.wait`) finished with an error.

    Attributes:
        correlation_id: Operation ID of the command.
        exception: Error details reported by iikoCloud.
        error_reason: Error reason code reported by iikoCloud.
        status: The full command status object.
    """

    def __init__(self, correlation_id: str, *, exception: Any, error_reason: Any, status: Any) -> None:
        self.correlation_id = correlation_id
        self.exception = exception
        self.error_reason = error_reason
        self.status = status
        details = exception.get("message") if isinstance(exception, dict) else getattr(exception, "message", None)
        message = details or exception or error_reason or "unknown error"
        super().__init__(f"Command {correlation_id} failed: {message}")


class CommandTimeout(IikoError, TimeoutError):  # noqa: N818
    """An asynchronous command did not finish within the given time."""

    def __init__(self, correlation_id: str, timeout: float) -> None:
        self.correlation_id = correlation_id
        self.timeout = timeout
        super().__init__(f"Command {correlation_id} did not finish in {timeout:g} s")


_BY_STATUS: dict[int, type[IikoApiError]] = {
    400: BadRequest,
    401: Unauthorized,
    403: Forbidden,
    404: NotFound,
    408: RequestTimeout,
    409: Conflict,
    410: Gone,
    422: UnprocessableEntity,
    429: TooManyRequests,
}


def error_from_response(response: httpx2.Response) -> IikoApiError:
    """Build the matching :class:`IikoApiError` subclass from an error response.

    Understands both error formats used by iikoCloud: ``{correlationId, errorDescription, error}``
    (iikoTransport API) and ``{message, details}`` (inventory, finance, nomenclature and other newer APIs).
    """
    cls = _BY_STATUS.get(response.status_code)
    if cls is None:
        cls = ServerError if response.status_code >= 500 else IikoApiError  # noqa: PLR2004
    try:
        body = json.loads(response.content) if response.content else None
    except ValueError:
        body = None
    if isinstance(body, dict):
        description = body.get("errorDescription") or body.get("message") or body.get("error") or ""
        return cls(
            response,
            description=str(description),
            error=body.get("error") if body.get("errorDescription") else None,
            correlation_id=body.get("correlationId"),
            details=body.get("details"),
        )
    text = response.text.strip()
    return cls(response, description=text[:500] or response.reason_phrase)


__all__ = [
    "BadRequest",
    "CommandFailed",
    "CommandTimeout",
    "Conflict",
    "Forbidden",
    "Gone",
    "IikoApiError",
    "IikoError",
    "IikoNetworkError",
    "NotFound",
    "RequestTimeout",
    "ResponseValidationError",
    "ServerError",
    "TooManyRequests",
    "Unauthorized",
    "UnprocessableEntity",
    "error_from_response",
]
