from __future__ import annotations

import json

from iikocloudapi import parse_webhook, verify_webhook_token
from iikocloudapi.webhooks import StopListUpdateEvent, UnknownWebhookEvent

EVENTS = [
    {
        "eventType": "StopListUpdate",
        "eventTime": "2024-01-02 03:04:05.678",
        "organizationId": "org",
        "correlationId": "c",
        "eventInfo": {"terminalGroupsStopListsUpdates": [{"id": "tg", "isFull": True}]},
    },
    {"eventType": "QuantumEntanglement", "organizationId": "org", "eventInfo": {"x": 1}},
]


def test_parse_known_and_unknown_events() -> None:
    known, unknown = parse_webhook(json.dumps(EVENTS).encode())
    assert isinstance(known, StopListUpdateEvent)
    assert known.organization_id == "org"
    assert isinstance(unknown, UnknownWebhookEvent)
    assert unknown.event_type == "QuantumEntanglement"
    assert unknown.event_info == {"x": 1}


def test_parse_decoded_json() -> None:
    assert len(parse_webhook(EVENTS)) == 2


def test_verify_token() -> None:
    assert verify_webhook_token("secret", "secret")
    assert verify_webhook_token("Bearer secret", "secret")
    assert not verify_webhook_token("Bearer other", "secret")
    assert not verify_webhook_token(None, "secret")
    assert not verify_webhook_token("secret", "")
