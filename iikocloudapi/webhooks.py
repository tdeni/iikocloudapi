"""Parsing and verifying incoming iikoCloud webhooks.

Configure the receiver with ``iiko.webhooks.update_settings(...)``; iikoCloud then POSTs a JSON array of events to
``webHooksUri`` and passes the configured ``authToken`` in the ``Authorization`` header.
"""

from __future__ import annotations

import hmac
from typing import Any

from pydantic import TypeAdapter

from iikocloudapi._base import LENIENT_CONTEXT
from iikocloudapi.models.webhooks import (
    DeliveryOrderErrorEvent,
    DeliveryOrderUpdateEvent,
    PersonalShiftEvent,
    ReserveErrorEvent,
    ReserveUpdateEvent,
    StopListUpdateEvent,
    TableOrderErrorEvent,
    TableOrderUpdateEvent,
    UnknownWebhookEvent,
    WebhookEvent,
)

_EVENTS: TypeAdapter[list[WebhookEvent]] = TypeAdapter(list[WebhookEvent])


def parse_webhook(body: bytes | str | list[Any]) -> list[WebhookEvent]:
    """Parse the body of a webhook request into typed events.

    Args:
        body: Raw request body (``bytes``/``str``) or already decoded JSON.

    Returns:
        The events, each an instance of one of the ``*Event`` models (``UnknownWebhookEvent`` for event types
        added to iikoCloud after this library was released).

    Example:
        ```python
        for event in parse_webhook(await request.body()):
            match event:
                case DeliveryOrderUpdateEvent():
                    ...
        ```
    """
    if isinstance(body, bytes | bytearray | str):
        return _EVENTS.validate_json(body, context=LENIENT_CONTEXT)
    return _EVENTS.validate_python(body, context=LENIENT_CONTEXT)


def verify_webhook_token(authorization: str | None, expected: str) -> bool:
    """Check the ``Authorization`` header of a webhook request against the configured ``authToken``.

    Accepts both the bare token and ``Bearer <token>``; compares in constant time.
    """
    if not authorization or not expected:
        return False
    token = authorization.removeprefix("Bearer ").strip()
    return hmac.compare_digest(token.encode(), expected.encode())


__all__ = [
    "DeliveryOrderErrorEvent",
    "DeliveryOrderUpdateEvent",
    "PersonalShiftEvent",
    "ReserveErrorEvent",
    "ReserveUpdateEvent",
    "StopListUpdateEvent",
    "TableOrderErrorEvent",
    "TableOrderUpdateEvent",
    "UnknownWebhookEvent",
    "WebhookEvent",
    "parse_webhook",
    "verify_webhook_token",
]
