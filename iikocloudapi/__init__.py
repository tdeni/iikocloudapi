"""Fully typed async client for the iikoCloud API.

```python
from iikocloudapi import AppAuth, IikoCloud

async with IikoCloud(auth=AppAuth(api_key=..., app_id=..., client_secret=...)) as iiko:
    organizations = await iiko.organizations()
```
"""

from iikocloudapi._auth import ApiLoginAuth, AppAuth, IikoAuth
from iikocloudapi._base import IikoDateTime, IikoModel, IsoDateTime, OpenIntEnum, OpenStrEnum, OrganizationItems
from iikocloudapi._client import API_EU, API_RU, DEFAULT_TIMEOUT, IikoCloud
from iikocloudapi._errors import (
    BadRequest,
    CommandFailed,
    CommandTimeout,
    Conflict,
    Forbidden,
    Gone,
    IikoApiError,
    IikoError,
    IikoNetworkError,
    NotFound,
    RequestTimeout,
    ResponseValidationError,
    ServerError,
    TooManyRequests,
    Unauthorized,
    UnprocessableEntity,
)
from iikocloudapi._version import __version__
from iikocloudapi.webhooks import WebhookEvent, parse_webhook, verify_webhook_token

__all__ = [
    "API_EU",
    "API_RU",
    "DEFAULT_TIMEOUT",
    "ApiLoginAuth",
    "AppAuth",
    "BadRequest",
    "CommandFailed",
    "CommandTimeout",
    "Conflict",
    "Forbidden",
    "Gone",
    "IikoApiError",
    "IikoAuth",
    "IikoCloud",
    "IikoDateTime",
    "IikoError",
    "IikoModel",
    "IikoNetworkError",
    "IsoDateTime",
    "NotFound",
    "OpenIntEnum",
    "OpenStrEnum",
    "OrganizationItems",
    "RequestTimeout",
    "ResponseValidationError",
    "ServerError",
    "TooManyRequests",
    "Unauthorized",
    "UnprocessableEntity",
    "WebhookEvent",
    "__version__",
    "parse_webhook",
    "verify_webhook_token",
]
