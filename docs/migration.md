# Migrating from 0.4

Version 1.0 is generated from the iikoCloud OpenAPI specification. The ideas are the same (an async client with
pydantic models), but almost every name changed to follow the API. Plan the upgrade as a rewrite of the
integration layer; the steps below cover the typical changes.

## The client

```python
# 0.4
from iikocloudapi import Client, iikoCloudApi

iiko = iikoCloudApi(Client("api-login"))

# 1.0
from iikocloudapi import ApiLoginAuth, AppAuth, IikoCloud

iiko = IikoCloud(auth=ApiLoginAuth("api-login"))  # same credentials, deprecated by iikoCloud
iiko = IikoCloud(auth=AppAuth(api_key="...", app_id="...", client_secret="..."))  # recommended
```

- Close the client: `async with IikoCloud(...) as iiko:` or `await iiko.aclose()`.
- `Client(session=...)` is now `IikoCloud(http_client=...)` and takes an `httpx2.AsyncClient`
  (the library moved from `httpx` to its maintained continuation, [httpx2](https://github.com/pydantic/httpx2)).
- `Client(headers=...)` is now `IikoCloud(headers=...)`; `Content-Type` and `Timeout` are set for you.
- Several clients with different API logins no longer share a token (0.4 leaked the token between them).

## Methods

All arguments are keyword-only.

| 0.4 | 1.0 |
| --- | --- |
| `iiko.auth.access_token(api_login)` | handled by `ApiLoginAuth`; `iiko.access_token(...)` is the v2 endpoint |
| `iiko.organizations(...)` | `iiko.organizations(...)` |
| `iiko.organizations.settings(...)` | `iiko.organizations.settings(...)` |
| `iiko.terminal_groups(...)` | `iiko.terminal_groups(...)` |
| `iiko.terminal_groups.is_alive(...)` | `iiko.terminal_groups.is_alive(...)` |
| `iiko.terminal_groups.awake(...)` | `iiko.terminal_groups.awake(...)` |
| `iiko.dictionaries.cancel_causes(...)` | `iiko.cancel_causes(...)` |
| `iiko.dictionaries.order_types(...)` | `iiko.deliveries.order_types(...)` |
| `iiko.dictionaries.discounts(...)` | `iiko.discounts(...)` |
| `iiko.dictionaries.payment_types(...)` | `iiko.payment_types(...)` |
| `iiko.dictionaries.removal_types(...)` | `iiko.removal_types(...)` |
| `iiko.dictionaries.tips_types()` | `iiko.tips_types()` |
| `iiko.menu()` | `iiko.menu()` |
| `iiko.menu.by_id(...)` | `iiko.menu.by_id(...)`: now `/api/menu/v3/by_id`, the response model is `MenuV3` |
| `iiko.menu.nomenclature(...)` | `iiko.nomenclature(...)` (deprecated by iikoCloud) |
| `iiko.menu.stop_lists(...)` | `iiko.stop_lists(...)` |
| `iiko.menu.stop_lists_check(...)` | `iiko.stop_lists.check(...)` |
| `iiko.menu.stop_lists_add(...)` | `iiko.stop_lists.add(...)` |
| `iiko.menu.stop_lists_remove(...)` | `iiko.stop_lists.remove(...)` |
| `iiko.menu.stop_lists_clear(...)` | `iiko.stop_lists.clear(...)` |
| `iiko.menu.combo(...)` | `iiko.combo(...)` |
| `iiko.menu.combo_calculate(...)` | `iiko.combo.calculate(...)` |
| `iiko.notifications.send(...)` | `iiko.notifications.send(body=OrderAttentionNotificationRequest(...))` |
| `iiko.operations.commands_status(...)` | `iiko.commands.status(...)`, or simply `iiko.wait(...)` |

Everything else in the API is new; see the [coverage table](reference/index.md).

## Models

- Model classes are named after the specification, for example `OrganizationsResponse` is now
  `GetOrganizationsResponse`, `CommandsStatusResponse` is `GetCommandStatusResponse` and `MenuByIdResponse` is
  `MenuV3`. Import them from `iikocloudapi.models`.
- All numbers are `Decimal` (0.4 used `float` in some places).
- Fields follow the specification exactly: some that were required are optional now and vice versa.
- Polymorphic objects are separate models (`SimpleOrganizationInfo`/`ExtendedOrganizationInfo` instead of one
  model with optional fields).

## Errors

`iikocloudapi.client.HTTPError` is replaced by [a hierarchy](guide/errors.md):

```python
# 0.4
except HTTPError as error:
    error.error_data.error_description

# 1.0
except IikoApiError as error:
    error.description, error.error, error.correlation_id, error.status_code
```

Network failures raise `IikoNetworkError` instead of `httpx` exceptions.

## Commands

Polling `commands_status` by hand is no longer needed:

```python
response = await iiko.order.close(organization_id=org_id, order_id=order_id)
await iiko.wait(response, organization_id=org_id)
```
