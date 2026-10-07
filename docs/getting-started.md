# Getting started

## Installation

```bash
pip install iikocloudapi
```

The library supports CPython 3.11 to 3.14, including the free-threaded build of 3.14.

## Credentials

iikoCloud authenticates *applications*. You need three values:

1. Register at the [iiko developer portal](https://public-api.iikoweb.ru/portal) and create an application. You get
   an **app ID** and a one-time **client secret**.
2. In iikoWeb, open **Integrations > API Keys** and generate an **API key** for the restaurant chain.

```python
from iikocloudapi import AppAuth

auth = AppAuth(api_key="...", app_id="...", client_secret="...")
```

If you only have an *API login* from iikoWeb, use the legacy authentication. iikoCloud marks it as deprecated, so
plan to move to `AppAuth`:

```python
from iikocloudapi import ApiLoginAuth

auth = ApiLoginAuth("api-login")
```

See [Authentication](guide/authentication.md) for details on tokens.

## The first request

```python
import asyncio

from iikocloudapi import AppAuth, IikoCloud


async def main() -> None:
    async with IikoCloud(auth=AppAuth(api_key="...", app_id="...", client_secret="...")) as iiko:
        organizations = await iiko.organizations()
        organization_ids = [org.id for org in organizations.organizations]

        groups = await iiko.terminal_groups(organization_ids=organization_ids)
        for organization in groups.terminal_groups:
            for group in organization.items:
                print(group.name, group.id)


asyncio.run(main())
```

`IikoCloud` holds a connection pool: create one per application and close it when the application stops
(`async with` or `await iiko.aclose()`).

## Client options

```python
from iikocloudapi import API_EU, IikoCloud

iiko = IikoCloud(
    auth=auth,
    base_url=API_EU,  # https://api-eu.iiko.services; the default is API_RU
    timeout=30,  # server-side timeout in seconds, see below
    headers={"X-Request-Source": "my-service"},
)
```

**Timeouts.** Many requests are answered by the restaurant's terminal, not by iikoCloud itself. The ``Timeout``
header tells iikoCloud how long to wait for the terminal (15 seconds by default). The library sends it with every
request and waits a few seconds longer on its side. Any method accepts `timeout=` to override it for one call:

```python
menu = await iiko.menu.by_id(external_menu_id=menu_id, organization_id=org_id, timeout=60)
```

**Your own HTTP client.** Pass an [`httpx2.AsyncClient`](https://github.com/pydantic/httpx2) to configure proxies,
transports or instrumentation. You are responsible for closing it.

```python
import httpx2

http = httpx2.AsyncClient(proxy="http://proxy:3128")
iiko = IikoCloud(auth=auth, http_client=http)
```
