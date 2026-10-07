# Calling endpoints

## Method names

The attribute path of a method is the endpoint URL without `/api/`, the version and the `iiko` segment of loyalty
URLs, in `snake_case`:

| Endpoint | Method |
| --- | --- |
| `/api/1/organizations` | `iiko.organizations()` |
| `/api/1/organizations/settings` | `iiko.organizations.settings()` |
| `/api/1/order/create` | `iiko.order.create()` |
| `/api/1/order/init_by_posOrder` | `iiko.order.init_by_pos_order()` |
| `/api/1/deliveries/drafts/lock` | `iiko.deliveries.drafts.lock()` |
| `/api/menu/v3/by_id` | `iiko.menu.by_id()` |
| `/api/1/loyalty/iiko/customer/wallet/hold` | `iiko.loyalty.customer.wallet.hold()` |
| `/api/inventory/v1/outgoing_invoice/list` | `iiko.inventory.outgoing_invoice.list()` |
| `/api/finance/v1/cash-flow-category/create` | `iiko.finance.cash_flow_category.create()` |

The [coverage table](../reference/index.md) lists all of them.

## Arguments

Every field of the request body is a keyword argument in `snake_case`. Required fields are required arguments,
optional fields default to `None` and are **not sent** when you leave them out:

```python
await iiko.organizations(return_additional_info=True)
# sends {"returnAdditionalInfo": true} to /api/1/organizations
```

Nested objects are models from `iikocloudapi.models`. Plain dictionaries work too, with either `camelCase` (as in
the iikoCloud documentation) or `snake_case` keys. Both are validated before the request is sent:

```python
from decimal import Decimal

from iikocloudapi.models import ProductOrderItem

await iiko.order.add_items(
    organization_id=org_id,
    order_id=order_id,
    items=[
        ProductOrderItem(product_id=soup_id, amount=Decimal(1), price=Decimal("320.00")),
        {"type": "Product", "productId": tea_id, "amount": 2, "price": 90},
    ],
)
```

### Validation

Request models are strict. These mistakes raise `pydantic.ValidationError` and nothing is sent:

- a field that does not exist (`credentials` instead of `customData`),
- an enum value that the API does not define (`delivery_status="Teleported"`),
- an unknown variant of a polymorphic object (`paymentTypeKind="Bitcoin"`),
- a missing required field or a value of the wrong type.

### Polymorphic objects

Payments, order items, customers, addresses and a few other objects come in several variants. Each variant is its
own model, and its type field is filled in for you:

```python
from iikocloudapi.models import CashPayment, ExternalPayment, ExternalPaymentAdditionalData

payments = [
    CashPayment(payment_type_id=cash_id, sum=Decimal("100")),
    ExternalPayment(
        payment_type_id=online_id,
        sum=Decimal("350"),
        is_processed_externally=True,
        payment_additional_data=ExternalPaymentAdditionalData(custom_data=acquirer_payment_id),
    ),
]
# [{"paymentTypeKind": "Cash", ...}, {"paymentTypeKind": "External", ..., "paymentAdditionalData": {"type": "External", ...}}]
```

### `None` and `null`

- Leaving out an optional argument or model field means "not sent".
- Setting a model field to `None` explicitly sends `null`.
- Some fields must always be present in the JSON but may be `null`. They default to `None` and are always sent,
  so you can simply omit them.

## Numbers and dates

- All numbers are `decimal.Decimal`. You can pass `int`, `float`, `str` or `Decimal`; they are sent as JSON numbers.
- Date-time fields accept `datetime` objects or strings and are sent in iikoCloud's `yyyy-MM-dd HH:mm:ss.fff` format.
  iikoCloud works in the organization's local time, so pass naive datetimes in that time zone.

## Raw requests

`iiko.request()` calls any path, for example an endpoint that appeared after your version of the library was
released. The body may contain models, `Decimal`s and datetimes; the decoded JSON is returned:

```python
data = await iiko.request("/api/1/brand_new_endpoint", {"organizationId": org_id})
```
