# Authentication

iikoCloud uses short-lived bearer tokens. An authentication strategy obtains a token, attaches it to every request
and refreshes it when needed. You never call the token endpoint yourself.

| Strategy | Endpoint | Credentials |
| --- | --- | --- |
| `AppAuth` | `/api/v2/access_token` | API key, app ID and client secret |
| `ApiLoginAuth` *(deprecated)* | `/api/1/access_token` | API login |

## Token lifecycle

- The token is requested on the first API call, not when the client is created.
- It is reused until shortly (60 seconds) before it expires. `AppAuth` tokens are JWTs and carry their expiry;
  tokens without an expiry are refreshed every 15 minutes.
- If iikoCloud answers `401 Unauthorized` anyway (for example, the token was revoked), the token is refreshed and
  the request is retried **once**. A second `401` raises [`Unauthorized`](errors.md).
- Concurrent requests share one token request.

```python
auth = AppAuth(api_key="...", app_id="...", client_secret="...")
iiko = IikoCloud(auth=auth)

await iiko.organizations()
print(auth.token)  # the current token
auth.invalidate()  # forget it; the next request gets a new one
```

One strategy instance can be shared by several `IikoCloud` clients, for example clients with different timeouts.

## Several API keys

Each restaurant chain has its own API key. Create one client per key; they do not share any state:

```python
clients = {chain: IikoCloud(auth=AppAuth(key, APP_ID, SECRET)) for chain, key in api_keys.items()}
```

## Custom strategies

Subclass `IikoAuth` to get tokens differently. For example, to share one token between worker processes, keep it
in Redis and override `token_request()`/`parse_token_response()`, or set `token_path` and `token_payload()` for
another token endpoint:

```python
from typing import Any

from iikocloudapi import IikoAuth


class PartnerAuth(IikoAuth):
    token_path = "/api/v2/access_token"

    def __init__(self, api_key: str, app_id: str, client_secret: str) -> None:
        super().__init__()
        self.credentials = {"apiKey": api_key, "appId": app_id, "clientSecret": client_secret}

    def token_payload(self) -> dict[str, Any]:
        return self.credentials
```

`IikoAuth` is an [`httpx2.Auth`](https://github.com/pydantic/httpx2), so you can also pass any other `httpx2.Auth`
to `IikoCloud(auth=...)`.
