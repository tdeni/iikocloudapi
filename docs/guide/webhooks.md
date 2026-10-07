# Webhooks

iikoCloud can notify your service about changes instead of being polled: delivery and table order updates,
reserve updates, stop list changes, personal shifts and errors.

## Configure

Webhook settings belong to an organization. Choose the URL, a secret token and the events you want:

```python
from iikocloudapi.models import DeliveryOrderWebHooksFilter, DeliveryStatus, WebHooksFilter, WebHookShortFilter

await iiko.webhooks.update_settings(
    organization_id=org_id,
    web_hooks_uri="https://example.com/iiko/webhooks",
    auth_token="long-random-secret",
    web_hooks_filter=WebHooksFilter(
        delivery_order_filter=DeliveryOrderWebHooksFilter(
            order_statuses=[DeliveryStatus.ON_WAY, DeliveryStatus.DELIVERED],
            errors=True,
        ),
        stop_list_update_filter=WebHookShortFilter(updates=True),
    ),
)

settings = await iiko.webhooks.settings(organization_id=org_id)
```

## Receive

iikoCloud POSTs a JSON array of events and passes `auth_token` in the `Authorization` header. Check the token with
`verify_webhook_token()` and parse the body with `parse_webhook()`:

```python
from iikocloudapi import parse_webhook, verify_webhook_token
from iikocloudapi.webhooks import DeliveryOrderUpdateEvent, StopListUpdateEvent, UnknownWebhookEvent

if not verify_webhook_token(request.headers.get("Authorization"), "long-random-secret"):
    return 401

for event in parse_webhook(body):
    match event:
        case DeliveryOrderUpdateEvent(event_info=info):
            ...
        case StopListUpdateEvent(organization_id=organization_id):
            ...
        case UnknownWebhookEvent(event_type=event_type):
            ...  # an event type added after this version was released
```

Answer with `200` quickly and do the heavy work in the background.

| Event | `event_info` |
| --- | --- |
| `DeliveryOrderUpdateEvent`, `DeliveryOrderErrorEvent` | `OrderInfo` |
| `TableOrderUpdateEvent`, `TableOrderErrorEvent` | `TableOrderInfo` |
| `ReserveUpdateEvent`, `ReserveErrorEvent` | `ReserveInfo` |
| `StopListUpdateEvent` | `WebHookOnStopListChangeData` |
| `PersonalShiftEvent` | `PersonalShift` |

A complete FastAPI receiver is in the [examples](../examples.md#webhook-receiver).
