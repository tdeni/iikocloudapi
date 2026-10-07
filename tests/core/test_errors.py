from __future__ import annotations

import httpx2
import pytest

from iikocloudapi import (
    BadRequest,
    Conflict,
    Forbidden,
    Gone,
    IikoApiError,
    NotFound,
    RequestTimeout,
    ServerError,
    TooManyRequests,
    Unauthorized,
    UnprocessableEntity,
)
from iikocloudapi._errors import error_from_response


def response(status: int, **kwargs: object) -> httpx2.Response:
    return httpx2.Response(status, request=httpx2.Request("POST", "https://x/api"), **kwargs)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("status", "cls"),
    [
        (400, BadRequest),
        (401, Unauthorized),
        (403, Forbidden),
        (404, NotFound),
        (408, RequestTimeout),
        (409, Conflict),
        (410, Gone),
        (422, UnprocessableEntity),
        (429, TooManyRequests),
        (500, ServerError),
        (502, ServerError),
        (418, IikoApiError),
    ],
)
def test_status_mapping(status: int, cls: type[IikoApiError]) -> None:
    error = error_from_response(response(status, json={"errorDescription": "x"}))
    assert type(error) is cls
    assert error.status_code == status


def test_transport_error_format() -> None:
    error = error_from_response(
        response(400, json={"correlationId": "c1", "errorDescription": "Bad org", "error": "ORG"})
    )
    assert (error.description, error.error, error.correlation_id) == ("Bad org", "ORG", "c1")
    assert str(error) == "400 ORG: Bad org (correlationId=c1)"


def test_newer_api_error_format() -> None:
    error = error_from_response(response(422, json={"message": "Invalid period", "details": {"from": "required"}}))
    assert error.description == "Invalid period"
    assert error.details == {"from": "required"}
    assert error.error is None
    assert str(error) == "422 Unprocessable Content: Invalid period"


def test_non_json_error_body() -> None:
    error = error_from_response(response(502, text="Bad gateway from nginx"))
    assert error.description == "Bad gateway from nginx"
    empty = error_from_response(response(503))
    assert empty.description == "Service Unavailable"


def test_retry_after() -> None:
    error = error_from_response(response(429, json={"message": "slow down"}, headers={"Retry-After": "7"}))
    assert isinstance(error, TooManyRequests)
    assert error.retry_after == 7
    assert error_from_response(response(429, headers={"Retry-After": "soon"})).retry_after is None  # type: ignore[union-attr]
