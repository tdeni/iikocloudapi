"""Receive iikoCloud webhooks with FastAPI.

Register the receiver once (``register()`` below), then run it:

    IIKO_WEBHOOK_TOKEN=... uvicorn examples.webhook_receiver:app --port 8000

iikoCloud expects a ``200`` answer quickly, so do the heavy work in the background.
"""

from __future__ import annotations

import asyncio
import os

from fastapi import FastAPI, Request, Response

from iikocloudapi import IikoCloud, parse_webhook, verify_webhook_token
from iikocloudapi.models import (
    DeliveryOrderWebHooksFilter,
    DeliveryStatus,
    OrderStatus,
    TableOrderWebHookFilter,
    WebHooksFilter,
    WebHookShortFilter,
)
from iikocloudapi.webhooks import (
    DeliveryOrderUpdateEvent,
    StopListUpdateEvent,
    TableOrderUpdateEvent,
    UnknownWebhookEvent,
)

try:
    from examples._env import client_from_env, env
except ImportError:  # pragma: no cover
    from _env import client_from_env, env  # type: ignore[no-redef]

WEBHOOK_TOKEN = os.environ.get("IIKO_WEBHOOK_TOKEN", "change-me")

app = FastAPI()


@app.post("/iiko/webhooks")
async def receive(request: Request) -> Response:
    if not verify_webhook_token(request.headers.get("Authorization"), WEBHOOK_TOKEN):
        return Response(status_code=401)
    for event in parse_webhook(await request.body()):
        match event:
            case DeliveryOrderUpdateEvent(event_info=info) if info and info.order:
                print(f"delivery {info.id}: {info.order.status}")
            case TableOrderUpdateEvent(event_info=info) if info and info.order:
                print(f"table order {info.id}: {info.order.status}")
            case StopListUpdateEvent(organization_id=organization_id):
                print(f"stop list changed in {organization_id}")
            case UnknownWebhookEvent(event_type=event_type):
                print(f"event {event_type} is not known to this version of iikocloudapi")
            case _:
                pass
    return Response(status_code=200)


async def register(iiko: IikoCloud, *, organization_id: str, url: str) -> None:
    """Point the organization's webhooks to ``url`` and choose which events to receive."""
    await iiko.webhooks.update_settings(
        organization_id=organization_id,
        web_hooks_uri=url,
        auth_token=WEBHOOK_TOKEN,
        web_hooks_filter=WebHooksFilter(
            delivery_order_filter=DeliveryOrderWebHooksFilter(
                order_statuses=[DeliveryStatus.ON_WAY, DeliveryStatus.DELIVERED, DeliveryStatus.CANCELLED],
                errors=True,
            ),
            table_order_filter=TableOrderWebHookFilter(order_statuses=[OrderStatus.CLOSED], errors=True),
            stop_list_update_filter=WebHookShortFilter(updates=True),
        ),
    )


if __name__ == "__main__":

    async def run() -> None:
        async with client_from_env() as iiko:
            await register(iiko, organization_id=env("IIKO_ORGANIZATION_ID"), url=env("IIKO_WEBHOOK_URL"))
            print("Webhook settings updated")

    asyncio.run(run())
