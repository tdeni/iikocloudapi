# iikocloudapi

A fully typed async Python client for the [iikoCloud API](https://api-ru.iiko.services/docs), generated from the
official OpenAPI specification.

```python
from iikocloudapi import AppAuth, IikoCloud

async with IikoCloud(auth=AppAuth(api_key="...", app_id="...", client_secret="...")) as iiko:
    organizations = await iiko.organizations()
    for org in organizations.organizations:
        print(org.id, org.name)
```

## Why this library

- **Every endpoint.** All 324 current endpoints: deliveries, table orders, reserves, loyalty, menu, inventory,
  finance, nomenclature, employees, reports and more. The method name mirrors the URL, so the
  [official documentation](https://api-ru.iiko.services/docs) tells you which method to call:
  `/api/1/order/create` is `iiko.order.create(...)`.
- **Typed models for every request and response**, with editor autocompletion and documentation for every field.
- **Strict requests, tolerant responses.** A typo in a field name or an unknown enum value raises an error *before*
  the request is sent. New fields and values added by iikoCloud never break parsing of responses.
- **Exact money.** All numbers are `Decimal`.
- **Batteries included:** token refresh, a typed exception hierarchy, a helper that waits for
  [asynchronous commands](guide/commands.md), and [webhook](guide/webhooks.md) parsing.
- **Always up to date.** The specification is checked weekly; changes arrive as a reviewed pull request.

## Next steps

- [Getting started](getting-started.md): install, authenticate, make the first request.
- [Calling endpoints](guide/requests.md): how methods and models map to the API.
- [Examples](examples.md): table orders with online payment, deliveries, menu sync, webhooks.
- [API coverage](reference/index.md): every endpoint and its method.
- [Migrating from 0.4](migration.md).
