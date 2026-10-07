# iikocloudapi

[![PyPI](https://img.shields.io/pypi/v/iikocloudapi)](https://pypi.org/project/iikocloudapi/)
[![Python](https://img.shields.io/pypi/pyversions/iikocloudapi)](https://pypi.org/project/iikocloudapi/)
[![CI](https://github.com/tdeni/iikocloudapi/actions/workflows/ci.yml/badge.svg)](https://github.com/tdeni/iikocloudapi/actions/workflows/ci.yml)
[![Docs](https://img.shields.io/badge/docs-tdeni.github.io-orange)](https://tdeni.github.io/iikocloudapi/)
[![iikoCloud API](https://img.shields.io/badge/iikoCloud_API-full_coverage-success)](https://tdeni.github.io/iikocloudapi/reference/)
[![License](https://img.shields.io/pypi/l/iikocloudapi)](https://github.com/tdeni/iikocloudapi/blob/master/LICENCE)

A fully typed async Python client for the [iikoCloud API](https://api-ru.iiko.services/docs), generated from the
official OpenAPI specification.

- **Every endpoint**: deliveries, table orders, reserves, loyalty, menu, inventory, finance, nomenclature,
  employees, reports. The method name mirrors the URL: `/api/1/order/create` is `iiko.order.create(...)`.
- **Typed models** for every request and response, with documentation for every field.
- **Strict requests, tolerant responses**: a typo in a field name fails *before* the request is sent; new fields
  and enum values from iikoCloud never break parsing.
- **Exact money**: all numbers are `Decimal`.
- **Batteries included**: token refresh, typed errors, waiting for asynchronous commands, webhook parsing.
- **Always up to date**: the specification is checked weekly.

## Installation

```bash
pip install iikocloudapi
```

Python 3.11 to 3.14.

## Quickstart

```python
import asyncio
from decimal import Decimal

from iikocloudapi import AppAuth, IikoCloud
from iikocloudapi.models import CashPayment, ProductOrderItem, TableOrder


async def main() -> None:
    auth = AppAuth(api_key="...", app_id="...", client_secret="...")
    async with IikoCloud(auth=auth) as iiko:
        organizations = await iiko.organizations()
        org_id = organizations.organizations[0].id

        groups = await iiko.terminal_groups(organization_ids=[org_id])
        group_id = groups.terminal_groups[0].items[0].id

        created = await iiko.order.create(
            organization_id=org_id,
            terminal_group_id=group_id,
            order=TableOrder(
                table_ids=["..."],
                items=[ProductOrderItem(product_id="...", amount=Decimal(1), price=Decimal("450.00"))],
                payments=[CashPayment(payment_type_id="...", sum=Decimal("450.00"))],
            ),
        )
        await iiko.wait(created, organization_id=org_id)  # order creation is an asynchronous command


asyncio.run(main())
```

More in the [documentation](https://tdeni.github.io/iikocloudapi/) and the [examples](https://github.com/tdeni/iikocloudapi/tree/master/examples):
table orders paid online (pay first and cook first), deliveries, menu sync with stop lists, a webhook receiver.

## Handling errors

```python
from iikocloudapi import BadRequest, CommandFailed, IikoNetworkError

try:
    created = await iiko.deliveries.create(organization_id=org_id, terminal_group_id=group_id, order=order)
    await iiko.wait(created, organization_id=org_id)
except BadRequest as error:
    print(error.description, error.correlation_id)
except CommandFailed as error:
    print("The terminal rejected the order:", error.exception)
except IikoNetworkError:
    ...
```

## API coverage

<!-- coverage:start -->

**324 endpoints**: every iikoCloud API endpoint that is not superseded by a newer version.

| Section | Endpoints |
| --- | ---: |
| General | 34 |
| Delivery | 43 |
| Orders | 12 |
| Reserves | 12 |
| WebHooks | 2 |
| Licenses | 1 |
| Loyalty and discounts | 27 |
| Inventory | 96 |
| Finance | 34 |
| Nomenclature | 41 |
| Employees | 13 |
| Reports | 5 |
| Terminals | 2 |
| Platform | 2 |

<details><summary><b>General</b></summary>

| Endpoint | Method |
| --- | --- |
| `/api/v2/access_token` | `iiko.access_token()` |
| `/api/1/notifications/send` | `iiko.notifications.send()` |
| `/api/1/organizations` | `iiko.organizations()` |
| `/api/1/organizations/settings` | `iiko.organizations.settings()` |
| `/api/1/terminal_groups` | `iiko.terminal_groups()` |
| `/api/1/terminal_groups/awake` | `iiko.terminal_groups.awake()` |
| `/api/1/terminal_groups/is_alive` | `iiko.terminal_groups.is_alive()` |
| `/api/1/cancel_causes` | `iiko.cancel_causes()` |
| `/api/1/deliveries/order_types` | `iiko.deliveries.order_types()` |
| `/api/1/discounts` | `iiko.discounts()` |
| `/api/1/payment_types` | `iiko.payment_types()` |
| `/api/1/removal_types` | `iiko.removal_types()` |
| `/api/1/tips_types` | `iiko.tips_types()` |
| `/api/1/combo` | `iiko.combo()` |
| `/api/1/combo/calculate` | `iiko.combo.calculate()` |
| `/api/2/menu` | `iiko.menu()` |
| `/api/menu/v3/by_id` | `iiko.menu.by_id()` |
| `/api/1/nomenclature` | `iiko.nomenclature()` |
| `/api/1/stop_lists` | `iiko.stop_lists()` |
| `/api/1/stop_lists/add` | `iiko.stop_lists.add()` |
| `/api/1/stop_lists/check` | `iiko.stop_lists.check()` |
| `/api/1/stop_lists/clear` | `iiko.stop_lists.clear()` |
| `/api/1/stop_lists/remove` | `iiko.stop_lists.remove()` |
| `/api/1/commands/status` | `iiko.commands.status()` |
| `/api/1/employees/couriers` | `iiko.employees.couriers()` |
| `/api/1/employees/couriers/active_location` | `iiko.employees.couriers.active_location()` |
| `/api/1/employees/couriers/active_location/by_terminal` | `iiko.employees.couriers.active_location.by_terminal()` |
| `/api/1/employees/couriers/by_role` | `iiko.employees.couriers.by_role()` |
| `/api/1/employees/couriers/locations/by_time_offset` | `iiko.employees.couriers.locations.by_time_offset()` |
| `/api/1/employees/info` | `iiko.employees.info()` |
| `/api/1/employees/shift/clockin` | `iiko.employees.shift.clockin()` |
| `/api/1/employees/shift/clockout` | `iiko.employees.shift.clockout()` |
| `/api/1/employees/shift/is_open` | `iiko.employees.shift.is_open()` |
| `/api/1/employees/shifts/by_courier` | `iiko.employees.shifts.by_courier()` |

</details>

<details><summary><b>Delivery</b></summary>

| Endpoint | Method |
| --- | --- |
| `/api/1/deliveries/add_items` | `iiko.deliveries.add_items()` |
| `/api/1/deliveries/add_payments` | `iiko.deliveries.add_payments()` |
| `/api/1/deliveries/cancel` | `iiko.deliveries.cancel()` |
| `/api/1/deliveries/cancel_confirmation` | `iiko.deliveries.cancel_confirmation()` |
| `/api/1/deliveries/change_comment` | `iiko.deliveries.change_comment()` |
| `/api/1/deliveries/change_complete_before` | `iiko.deliveries.change_complete_before()` |
| `/api/1/deliveries/change_delivery_point` | `iiko.deliveries.change_delivery_point()` |
| `/api/1/deliveries/change_driver_info` | `iiko.deliveries.change_driver_info()` |
| `/api/1/deliveries/change_external_data` | `iiko.deliveries.change_external_data()` |
| `/api/1/deliveries/change_operator` | `iiko.deliveries.change_operator()` |
| `/api/1/deliveries/change_payments` | `iiko.deliveries.change_payments()` |
| `/api/1/deliveries/change_service_type` | `iiko.deliveries.change_service_type()` |
| `/api/1/deliveries/close` | `iiko.deliveries.close()` |
| `/api/1/deliveries/confirm` | `iiko.deliveries.confirm()` |
| `/api/1/deliveries/create` | `iiko.deliveries.create()` |
| `/api/1/deliveries/print_delivery_bill` | `iiko.deliveries.print_delivery_bill()` |
| `/api/1/deliveries/update_order_courier` | `iiko.deliveries.update_order_courier()` |
| `/api/1/deliveries/update_order_delivery_status` | `iiko.deliveries.update_order_delivery_status()` |
| `/api/1/deliveries/update_order_payments` | `iiko.deliveries.update_order_payments()` |
| `/api/1/deliveries/update_order_problem` | `iiko.deliveries.update_order_problem()` |
| `/api/1/deliveries/update_tracking_link` | `iiko.deliveries.update_tracking_link()` |
| `/api/1/order/print_bill` | `iiko.order.print_bill()` |
| `/api/1/deliveries/by_delivery_date_and_phone` | `iiko.deliveries.by_delivery_date_and_phone()` |
| `/api/1/deliveries/by_delivery_date_and_source_key_and_filter` | `iiko.deliveries.by_delivery_date_and_source_key_and_filter()` |
| `/api/1/deliveries/by_delivery_date_and_status` | `iiko.deliveries.by_delivery_date_and_status()` |
| `/api/1/deliveries/by_id` | `iiko.deliveries.by_id()` |
| `/api/1/deliveries/by_revision` | `iiko.deliveries.by_revision()` |
| `/api/1/deliveries/history/by_delivery_date_and_phone` | `iiko.deliveries.history.by_delivery_date_and_phone()` |
| `/api/1/cities` | `iiko.cities()` |
| `/api/1/regions` | `iiko.regions()` |
| `/api/1/streets/by_city` | `iiko.streets.by_city()` |
| `/api/1/streets/by_id` | `iiko.streets.by_id()` |
| `/api/1/delivery_restrictions` | `iiko.delivery_restrictions()` |
| `/api/1/delivery_restrictions/allowed` | `iiko.delivery_restrictions.allowed()` |
| `/api/1/marketing_sources` | `iiko.marketing_sources()` |
| `/api/1/deliveries/drafts/by_filter` | `iiko.deliveries.drafts.by_filter()` |
| `/api/1/deliveries/drafts/by_id` | `iiko.deliveries.drafts.by_id()` |
| `/api/1/deliveries/drafts/commit` | `iiko.deliveries.drafts.commit()` |
| `/api/1/deliveries/drafts/create` | `iiko.deliveries.drafts.create()` |
| `/api/1/deliveries/drafts/delete` | `iiko.deliveries.drafts.delete()` |
| `/api/1/deliveries/drafts/lock` | `iiko.deliveries.drafts.lock()` |
| `/api/1/deliveries/drafts/save` | `iiko.deliveries.drafts.save()` |
| `/api/1/deliveries/drafts/unlock` | `iiko.deliveries.drafts.unlock()` |

</details>

<details><summary><b>Orders</b></summary>

| Endpoint | Method |
| --- | --- |
| `/api/1/order/add_customer` | `iiko.order.add_customer()` |
| `/api/1/order/add_items` | `iiko.order.add_items()` |
| `/api/1/order/add_payments` | `iiko.order.add_payments()` |
| `/api/1/order/by_id` | `iiko.order.by_id()` |
| `/api/1/order/by_table` | `iiko.order.by_table()` |
| `/api/1/order/cancel` | `iiko.order.cancel()` |
| `/api/1/order/change_external_data` | `iiko.order.change_external_data()` |
| `/api/1/order/change_payments` | `iiko.order.change_payments()` |
| `/api/1/order/close` | `iiko.order.close()` |
| `/api/1/order/create` | `iiko.order.create()` |
| `/api/1/order/init_by_posOrder` | `iiko.order.init_by_pos_order()` |
| `/api/1/order/init_by_table` | `iiko.order.init_by_table()` |

</details>

<details><summary><b>Reserves</b></summary>

| Endpoint | Method |
| --- | --- |
| `/api/1/reserve/add_items` | `iiko.reserve.add_items()` |
| `/api/1/reserve/add_payments` | `iiko.reserve.add_payments()` |
| `/api/1/reserve/available_organizations` | `iiko.reserve.available_organizations()` |
| `/api/1/reserve/available_restaurant_sections` | `iiko.reserve.available_restaurant_sections()` |
| `/api/1/reserve/available_terminal_groups` | `iiko.reserve.available_terminal_groups()` |
| `/api/1/reserve/cancel` | `iiko.reserve.cancel()` |
| `/api/1/reserve/change_estimated_start_time` | `iiko.reserve.change_estimated_start_time()` |
| `/api/1/reserve/change_items` | `iiko.reserve.change_items()` |
| `/api/1/reserve/change_tables` | `iiko.reserve.change_tables()` |
| `/api/1/reserve/create` | `iiko.reserve.create()` |
| `/api/1/reserve/restaurant_sections_workload` | `iiko.reserve.restaurant_sections_workload()` |
| `/api/1/reserve/status_by_id` | `iiko.reserve.status_by_id()` |

</details>

<details><summary><b>WebHooks</b></summary>

| Endpoint | Method |
| --- | --- |
| `/api/1/webhooks/settings` | `iiko.webhooks.settings()` |
| `/api/1/webhooks/update_settings` | `iiko.webhooks.update_settings()` |

</details>

<details><summary><b>Licenses</b></summary>

| Endpoint | Method |
| --- | --- |
| `/api/licenses/v2/list` | `iiko.licenses.list()` |

</details>

<details><summary><b>Loyalty and discounts</b></summary>

| Endpoint | Method |
| --- | --- |
| `/api/1/loyalty/iiko/calculate` | `iiko.loyalty.calculate()` |
| `/api/1/loyalty/iiko/coupons/by_series` | `iiko.loyalty.coupons.by_series()` |
| `/api/1/loyalty/iiko/coupons/info` | `iiko.loyalty.coupons.info()` |
| `/api/1/loyalty/iiko/coupons/series` | `iiko.loyalty.coupons.series()` |
| `/api/1/loyalty/iiko/manual_condition` | `iiko.loyalty.manual_condition()` |
| `/api/1/loyalty/iiko/program` | `iiko.loyalty.program()` |
| `/api/1/loyalty/iiko/customer_category` | `iiko.loyalty.customer_category()` |
| `/api/1/loyalty/iiko/customer_category/add` | `iiko.loyalty.customer_category.add()` |
| `/api/1/loyalty/iiko/customer_category/remove` | `iiko.loyalty.customer_category.remove()` |
| `/api/1/loyalty/iiko/customer/card/add` | `iiko.loyalty.customer.card.add()` |
| `/api/1/loyalty/iiko/customer/card/remove` | `iiko.loyalty.customer.card.remove()` |
| `/api/1/loyalty/iiko/customer/create_or_update` | `iiko.loyalty.customer.create_or_update()` |
| `/api/1/loyalty/iiko/customer/info` | `iiko.loyalty.customer.info()` |
| `/api/1/loyalty/iiko/customer/program/add` | `iiko.loyalty.customer.program.add()` |
| `/api/1/loyalty/iiko/customer/wallet/cancel_hold` | `iiko.loyalty.customer.wallet.cancel_hold()` |
| `/api/1/loyalty/iiko/customer/wallet/chargeoff` | `iiko.loyalty.customer.wallet.chargeoff()` |
| `/api/1/loyalty/iiko/customer/wallet/hold` | `iiko.loyalty.customer.wallet.hold()` |
| `/api/1/loyalty/iiko/customer/wallet/topup` | `iiko.loyalty.customer.wallet.topup()` |
| `/api/1/loyalty/iiko/delete_customers` | `iiko.loyalty.delete_customers()` |
| `/api/1/loyalty/iiko/get_counters` | `iiko.loyalty.get_counters()` |
| `/api/1/loyalty/iiko/restore_customers` | `iiko.loyalty.restore_customers()` |
| `/api/1/loyalty/iiko/check_sms_sending_possibility` | `iiko.loyalty.check_sms_sending_possibility()` |
| `/api/1/loyalty/iiko/check_sms_status` | `iiko.loyalty.check_sms_status()` |
| `/api/1/loyalty/iiko/message/send_email` | `iiko.loyalty.message.send_email()` |
| `/api/1/loyalty/iiko/message/send_sms` | `iiko.loyalty.message.send_sms()` |
| `/api/1/loyalty/iiko/customer/transactions/by_date` | `iiko.loyalty.customer.transactions.by_date()` |
| `/api/1/loyalty/iiko/customer/transactions/by_revision` | `iiko.loyalty.customer.transactions.by_revision()` |

</details>

<details><summary><b>Inventory</b></summary>

| Endpoint | Method |
| --- | --- |
| `/api/inventory/v1/incoming_invoice/cancel` | `iiko.inventory.incoming_invoice.cancel()` |
| `/api/inventory/v1/incoming_invoice/create` | `iiko.inventory.incoming_invoice.create()` |
| `/api/inventory/v1/incoming_invoice/get` | `iiko.inventory.incoming_invoice.get()` |
| `/api/inventory/v1/incoming_invoice/list` | `iiko.inventory.incoming_invoice.list()` |
| `/api/inventory/v1/incoming_invoice/modify/add_payment` | `iiko.inventory.incoming_invoice.modify.add_payment()` |
| `/api/inventory/v1/incoming_invoice/patch/set_payment_date` | `iiko.inventory.incoming_invoice.patch.set_payment_date()` |
| `/api/inventory/v1/incoming_invoice/post` | `iiko.inventory.incoming_invoice.post()` |
| `/api/inventory/v1/incoming_invoice/unpost` | `iiko.inventory.incoming_invoice.unpost()` |
| `/api/inventory/v1/incoming_invoice/update` | `iiko.inventory.incoming_invoice.update()` |
| `/api/inventory/v1/costings/calculate` | `iiko.inventory.costings.calculate()` |
| `/api/inventory/v1/outgoing_invoice/cancel` | `iiko.inventory.outgoing_invoice.cancel()` |
| `/api/inventory/v1/outgoing_invoice/create` | `iiko.inventory.outgoing_invoice.create()` |
| `/api/inventory/v1/outgoing_invoice/get` | `iiko.inventory.outgoing_invoice.get()` |
| `/api/inventory/v1/outgoing_invoice/list` | `iiko.inventory.outgoing_invoice.list()` |
| `/api/inventory/v1/outgoing_invoice/modify/add_payment` | `iiko.inventory.outgoing_invoice.modify.add_payment()` |
| `/api/inventory/v1/outgoing_invoice/patch/set_payment_date` | `iiko.inventory.outgoing_invoice.patch.set_payment_date()` |
| `/api/inventory/v1/outgoing_invoice/post` | `iiko.inventory.outgoing_invoice.post()` |
| `/api/inventory/v1/outgoing_invoice/unpost` | `iiko.inventory.outgoing_invoice.unpost()` |
| `/api/inventory/v1/outgoing_invoice/update` | `iiko.inventory.outgoing_invoice.update()` |
| `/api/inventory/v1/returned_invoice/cancel` | `iiko.inventory.returned_invoice.cancel()` |
| `/api/inventory/v1/returned_invoice/create` | `iiko.inventory.returned_invoice.create()` |
| `/api/inventory/v1/returned_invoice/get` | `iiko.inventory.returned_invoice.get()` |
| `/api/inventory/v1/returned_invoice/list` | `iiko.inventory.returned_invoice.list()` |
| `/api/inventory/v1/returned_invoice/post` | `iiko.inventory.returned_invoice.post()` |
| `/api/inventory/v1/returned_invoice/unpost` | `iiko.inventory.returned_invoice.unpost()` |
| `/api/inventory/v1/returned_invoice/update` | `iiko.inventory.returned_invoice.update()` |
| `/api/inventory/v1/incoming_returned_invoice/cancel` | `iiko.inventory.incoming_returned_invoice.cancel()` |
| `/api/inventory/v1/incoming_returned_invoice/create` | `iiko.inventory.incoming_returned_invoice.create()` |
| `/api/inventory/v1/incoming_returned_invoice/get` | `iiko.inventory.incoming_returned_invoice.get()` |
| `/api/inventory/v1/incoming_returned_invoice/list` | `iiko.inventory.incoming_returned_invoice.list()` |
| `/api/inventory/v1/incoming_returned_invoice/post` | `iiko.inventory.incoming_returned_invoice.post()` |
| `/api/inventory/v1/incoming_returned_invoice/unpost` | `iiko.inventory.incoming_returned_invoice.unpost()` |
| `/api/inventory/v1/incoming_returned_invoice/update` | `iiko.inventory.incoming_returned_invoice.update()` |
| `/api/inventory/v1/sales_document/cancel` | `iiko.inventory.sales_document.cancel()` |
| `/api/inventory/v1/sales_document/create` | `iiko.inventory.sales_document.create()` |
| `/api/inventory/v1/sales_document/get` | `iiko.inventory.sales_document.get()` |
| `/api/inventory/v1/sales_document/list` | `iiko.inventory.sales_document.list()` |
| `/api/inventory/v1/sales_document/post` | `iiko.inventory.sales_document.post()` |
| `/api/inventory/v1/sales_document/unpost` | `iiko.inventory.sales_document.unpost()` |
| `/api/inventory/v1/sales_document/update` | `iiko.inventory.sales_document.update()` |
| `/api/inventory/v1/writeoff_document/cancel` | `iiko.inventory.writeoff_document.cancel()` |
| `/api/inventory/v1/writeoff_document/create` | `iiko.inventory.writeoff_document.create()` |
| `/api/inventory/v1/writeoff_document/get` | `iiko.inventory.writeoff_document.get()` |
| `/api/inventory/v1/writeoff_document/list` | `iiko.inventory.writeoff_document.list()` |
| `/api/inventory/v1/writeoff_document/post` | `iiko.inventory.writeoff_document.post()` |
| `/api/inventory/v1/writeoff_document/unpost` | `iiko.inventory.writeoff_document.unpost()` |
| `/api/inventory/v1/writeoff_document/update` | `iiko.inventory.writeoff_document.update()` |
| `/api/inventory/v1/internal_transfer/cancel` | `iiko.inventory.internal_transfer.cancel()` |
| `/api/inventory/v1/internal_transfer/create` | `iiko.inventory.internal_transfer.create()` |
| `/api/inventory/v1/internal_transfer/get` | `iiko.inventory.internal_transfer.get()` |
| `/api/inventory/v1/internal_transfer/list` | `iiko.inventory.internal_transfer.list()` |
| `/api/inventory/v1/internal_transfer/post` | `iiko.inventory.internal_transfer.post()` |
| `/api/inventory/v1/internal_transfer/unpost` | `iiko.inventory.internal_transfer.unpost()` |
| `/api/inventory/v1/internal_transfer/update` | `iiko.inventory.internal_transfer.update()` |
| `/api/inventory/v1/production_document/cancel` | `iiko.inventory.production_document.cancel()` |
| `/api/inventory/v1/production_document/create` | `iiko.inventory.production_document.create()` |
| `/api/inventory/v1/production_document/get` | `iiko.inventory.production_document.get()` |
| `/api/inventory/v1/production_document/list` | `iiko.inventory.production_document.list()` |
| `/api/inventory/v1/production_document/post` | `iiko.inventory.production_document.post()` |
| `/api/inventory/v1/production_document/unpost` | `iiko.inventory.production_document.unpost()` |
| `/api/inventory/v1/production_document/update` | `iiko.inventory.production_document.update()` |
| `/api/inventory/v1/disassemble_document/cancel` | `iiko.inventory.disassemble_document.cancel()` |
| `/api/inventory/v1/disassemble_document/create` | `iiko.inventory.disassemble_document.create()` |
| `/api/inventory/v1/disassemble_document/get` | `iiko.inventory.disassemble_document.get()` |
| `/api/inventory/v1/disassemble_document/list` | `iiko.inventory.disassemble_document.list()` |
| `/api/inventory/v1/disassemble_document/post` | `iiko.inventory.disassemble_document.post()` |
| `/api/inventory/v1/disassemble_document/unpost` | `iiko.inventory.disassemble_document.unpost()` |
| `/api/inventory/v1/disassemble_document/update` | `iiko.inventory.disassemble_document.update()` |
| `/api/inventory/v1/transformation_document/cancel` | `iiko.inventory.transformation_document.cancel()` |
| `/api/inventory/v1/transformation_document/create` | `iiko.inventory.transformation_document.create()` |
| `/api/inventory/v1/transformation_document/get` | `iiko.inventory.transformation_document.get()` |
| `/api/inventory/v1/transformation_document/list` | `iiko.inventory.transformation_document.list()` |
| `/api/inventory/v1/transformation_document/post` | `iiko.inventory.transformation_document.post()` |
| `/api/inventory/v1/transformation_document/unpost` | `iiko.inventory.transformation_document.unpost()` |
| `/api/inventory/v1/transformation_document/update` | `iiko.inventory.transformation_document.update()` |
| `/api/inventory/v1/incoming_inventory/cancel` | `iiko.inventory.incoming_inventory.cancel()` |
| `/api/inventory/v1/incoming_inventory/create` | `iiko.inventory.incoming_inventory.create()` |
| `/api/inventory/v1/incoming_inventory/get` | `iiko.inventory.incoming_inventory.get()` |
| `/api/inventory/v1/incoming_inventory/list` | `iiko.inventory.incoming_inventory.list()` |
| `/api/inventory/v1/incoming_inventory/post` | `iiko.inventory.incoming_inventory.post()` |
| `/api/inventory/v1/incoming_inventory/unpost` | `iiko.inventory.incoming_inventory.unpost()` |
| `/api/inventory/v1/incoming_inventory/update` | `iiko.inventory.incoming_inventory.update()` |
| `/api/inventory/v1/counteragents/list` | `iiko.inventory.counteragents.list()` |
| `/api/inventory/v1/counteragents/pricelist/list` | `iiko.inventory.counteragents.pricelist.list()` |
| `/api/inventory/v1/organizations/settings/list` | `iiko.inventory.organizations.settings.list()` |
| `/api/inventory/v1/organizations/tree` | `iiko.inventory.organizations.tree()` |
| `/api/inventory/v1/stores/list` | `iiko.inventory.stores.list()` |
| `/api/inventory/v1/accounting_categories/get` | `iiko.inventory.accounting_categories.get()` |
| `/api/inventory/v1/accounting_categories/list` | `iiko.inventory.accounting_categories.list()` |
| `/api/inventory/v1/conceptions/get` | `iiko.inventory.conceptions.get()` |
| `/api/inventory/v1/conceptions/list` | `iiko.inventory.conceptions.list()` |
| `/api/inventory/v1/measure_units/get` | `iiko.inventory.measure_units.get()` |
| `/api/inventory/v1/measure_units/list` | `iiko.inventory.measure_units.list()` |
| `/api/inventory/v1/payment_types/get` | `iiko.inventory.payment_types.get()` |
| `/api/inventory/v1/payment_types/list` | `iiko.inventory.payment_types.list()` |
| `/api/inventory/v1/stock_balance/list` | `iiko.inventory.stock_balance.list()` |

</details>

<details><summary><b>Finance</b></summary>

| Endpoint | Method |
| --- | --- |
| `/api/finance/v1/incoming_service/cancel` | `iiko.finance.incoming_service.cancel()` |
| `/api/finance/v1/incoming_service/create` | `iiko.finance.incoming_service.create()` |
| `/api/finance/v1/incoming_service/get` | `iiko.finance.incoming_service.get()` |
| `/api/finance/v1/incoming_service/list` | `iiko.finance.incoming_service.list()` |
| `/api/finance/v1/incoming_service/post` | `iiko.finance.incoming_service.post()` |
| `/api/finance/v1/incoming_service/unpost` | `iiko.finance.incoming_service.unpost()` |
| `/api/finance/v1/incoming_service/update` | `iiko.finance.incoming_service.update()` |
| `/api/finance/v1/outgoing_service/cancel` | `iiko.finance.outgoing_service.cancel()` |
| `/api/finance/v1/outgoing_service/create` | `iiko.finance.outgoing_service.create()` |
| `/api/finance/v1/outgoing_service/get` | `iiko.finance.outgoing_service.get()` |
| `/api/finance/v1/outgoing_service/list` | `iiko.finance.outgoing_service.list()` |
| `/api/finance/v1/outgoing_service/post` | `iiko.finance.outgoing_service.post()` |
| `/api/finance/v1/outgoing_service/unpost` | `iiko.finance.outgoing_service.unpost()` |
| `/api/finance/v1/outgoing_service/update` | `iiko.finance.outgoing_service.update()` |
| `/api/finance/v1/account_transactions/list` | `iiko.finance.account_transactions.list()` |
| `/api/finance/v1/document_transactions/list` | `iiko.finance.document_transactions.list()` |
| `/api/finance/v1/account-type/list` | `iiko.finance.account_type.list()` |
| `/api/finance/v1/cash-flow-category/create` | `iiko.finance.cash_flow_category.create()` |
| `/api/finance/v1/cash-flow-category/delete` | `iiko.finance.cash_flow_category.delete()` |
| `/api/finance/v1/cash-flow-category/get` | `iiko.finance.cash_flow_category.get()` |
| `/api/finance/v1/cash-flow-category/list` | `iiko.finance.cash_flow_category.list()` |
| `/api/finance/v1/cash-flow-category/restore` | `iiko.finance.cash_flow_category.restore()` |
| `/api/finance/v1/cash-flow-category/update` | `iiko.finance.cash_flow_category.update()` |
| `/api/finance/v1/account/create` | `iiko.finance.account.create()` |
| `/api/finance/v1/account/delete` | `iiko.finance.account.delete()` |
| `/api/finance/v1/account/get` | `iiko.finance.account.get()` |
| `/api/finance/v1/account/list` | `iiko.finance.account.list()` |
| `/api/finance/v1/account/restore` | `iiko.finance.account.restore()` |
| `/api/finance/v1/account/update` | `iiko.finance.account.update()` |
| `/api/finance/v1/item-category/list` | `iiko.finance.item_category.list()` |
| `/api/finance/v1/tax-category/list` | `iiko.finance.tax_category.list()` |
| `/api/finance/v1/account-posting/list` | `iiko.finance.account_posting.list()` |
| `/api/finance/v1/balance-sheet/list` | `iiko.finance.balance_sheet.list()` |
| `/api/finance/v1/chart-of-accounts/list` | `iiko.finance.chart_of_accounts.list()` |

</details>

<details><summary><b>Nomenclature</b></summary>

| Endpoint | Method |
| --- | --- |
| `/api/nomenclature/v2/group/create` | `iiko.nomenclature.group.create()` |
| `/api/nomenclature/v2/group/delete` | `iiko.nomenclature.group.delete()` |
| `/api/nomenclature/v2/group/list` | `iiko.nomenclature.group.list()` |
| `/api/nomenclature/v2/group/restore` | `iiko.nomenclature.group.restore()` |
| `/api/nomenclature/v2/group/update` | `iiko.nomenclature.group.update()` |
| `/api/nomenclature/v2/product/create` | `iiko.nomenclature.product.create()` |
| `/api/nomenclature/v2/product/delete` | `iiko.nomenclature.product.delete()` |
| `/api/nomenclature/v2/product/list` | `iiko.nomenclature.product.list()` |
| `/api/nomenclature/v2/product/restore` | `iiko.nomenclature.product.restore()` |
| `/api/nomenclature/v2/product/update` | `iiko.nomenclature.product.update()` |
| `/api/nomenclature/v2/product/update_barcodes` | `iiko.nomenclature.product.update_barcodes()` |
| `/api/nomenclature/v2/assembly-chart/assembled` | `iiko.nomenclature.assembly_chart.assembled()` |
| `/api/nomenclature/v2/assembly-chart/create` | `iiko.nomenclature.assembly_chart.create()` |
| `/api/nomenclature/v2/assembly-chart/delete` | `iiko.nomenclature.assembly_chart.delete()` |
| `/api/nomenclature/v2/assembly-chart/get` | `iiko.nomenclature.assembly_chart.get()` |
| `/api/nomenclature/v2/assembly-chart/list` | `iiko.nomenclature.assembly_chart.list()` |
| `/api/nomenclature/v2/assembly-chart/prepared` | `iiko.nomenclature.assembly_chart.prepared()` |
| `/api/nomenclature/v2/assembly-chart/tree` | `iiko.nomenclature.assembly_chart.tree()` |
| `/api/nomenclature/v2/assembly-chart/update` | `iiko.nomenclature.assembly_chart.update()` |
| `/api/nomenclature/v1/product-scale/create` | `iiko.nomenclature.product_scale.create()` |
| `/api/nomenclature/v1/product-scale/delete` | `iiko.nomenclature.product_scale.delete()` |
| `/api/nomenclature/v1/product-scale/get` | `iiko.nomenclature.product_scale.get()` |
| `/api/nomenclature/v1/product-scale/list` | `iiko.nomenclature.product_scale.list()` |
| `/api/nomenclature/v1/product-scale/update` | `iiko.nomenclature.product_scale.update()` |
| `/api/nomenclature/v1/nomenclature/category/create` | `iiko.nomenclature.nomenclature.category.create()` |
| `/api/nomenclature/v1/nomenclature/category/delete` | `iiko.nomenclature.nomenclature.category.delete()` |
| `/api/nomenclature/v1/nomenclature/category/list` | `iiko.nomenclature.nomenclature.category.list()` |
| `/api/nomenclature/v1/nomenclature/category/restore` | `iiko.nomenclature.nomenclature.category.restore()` |
| `/api/nomenclature/v1/nomenclature/category/update` | `iiko.nomenclature.nomenclature.category.update()` |
| `/api/nomenclature/v1/allergen-group/list` | `iiko.nomenclature.allergen_group.list()` |
| `/api/nomenclature/v1/amount-unit/list` | `iiko.nomenclature.amount_unit.list()` |
| `/api/nomenclature/v1/container/list` | `iiko.nomenclature.container.list()` |
| `/api/nomenclature/v1/custom-category/list` | `iiko.nomenclature.custom_category.list()` |
| `/api/nomenclature/v1/menu/list` | `iiko.nomenclature.menu.list()` |
| `/api/nomenclature/v1/modifier-schema/list` | `iiko.nomenclature.modifier_schema.list()` |
| `/api/nomenclature/v1/outer_economic_activity_nomenclature_codes/get` | `iiko.nomenclature.outer_economic_activity_nomenclature_codes.get()` |
| `/api/nomenclature/v1/outer_economic_activity_nomenclature_codes/list` | `iiko.nomenclature.outer_economic_activity_nomenclature_codes.list()` |
| `/api/nomenclature/v1/place-type/list` | `iiko.nomenclature.place_type.list()` |
| `/api/nomenclature/v1/producer/list` | `iiko.nomenclature.producer.list()` |
| `/api/nomenclature/v1/product-size/list` | `iiko.nomenclature.product_size.list()` |
| `/api/nomenclature/v1/product-tag/list` | `iiko.nomenclature.product_tag.list()` |

</details>

<details><summary><b>Employees</b></summary>

| Endpoint | Method |
| --- | --- |
| `/api/employees/v1/employee/create` | `iiko.employees.employee.create()` |
| `/api/employees/v1/employee/fire` | `iiko.employees.employee.fire()` |
| `/api/employees/v1/employee/get` | `iiko.employees.employee.get()` |
| `/api/employees/v1/employee/list` | `iiko.employees.employee.list()` |
| `/api/employees/v1/employee/restore` | `iiko.employees.employee.restore()` |
| `/api/employees/v1/employee/update` | `iiko.employees.employee.update()` |
| `/api/employees/v1/positions/get` | `iiko.employees.positions.get()` |
| `/api/employees/v1/positions/list` | `iiko.employees.positions.list()` |
| `/api/employees/v1/attendance/create` | `iiko.employees.attendance.create()` |
| `/api/employees/v1/attendance/delete` | `iiko.employees.attendance.delete()` |
| `/api/employees/v1/attendance/list` | `iiko.employees.attendance.list()` |
| `/api/employees/v1/attendance/update` | `iiko.employees.attendance.update()` |
| `/api/employees/v1/attendance-type/list` | `iiko.employees.attendance_type.list()` |

</details>

<details><summary><b>Reports</b></summary>

| Endpoint | Method |
| --- | --- |
| `/api/reporting/v1/olap/columns/get` | `iiko.reporting.olap.columns.get()` |
| `/api/reporting/v1/olap/get` | `iiko.reporting.olap.get()` |
| `/api/reporting/v1/olap/presets/get` | `iiko.reporting.olap.presets.get()` |
| `/api/reporting/v1/olap/presets/list` | `iiko.reporting.olap.presets.list()` |
| `/api/reporting/v1/income-plan/list` | `iiko.reporting.income_plan.list()` |

</details>

<details><summary><b>Terminals</b></summary>

| Endpoint | Method |
| --- | --- |
| `/api/terminals/v1/terminals/list` | `iiko.terminals.terminals.list()` |
| `/api/terminals/v1/cash-registers/list` | `iiko.terminals.cash_registers.list()` |

</details>

<details><summary><b>Platform</b></summary>

| Endpoint | Method |
| --- | --- |
| `/api/platform/v1/events/list` | `iiko.platform.events.list()` |
| `/api/platform/v1/events/metadata/list` | `iiko.platform.events.metadata.list()` |

</details>

<!-- coverage:end -->

## Upgrading from 0.4

Version 1.0 is a rewrite: see the [migration guide](https://tdeni.github.io/iikocloudapi/migration/).

## Development

```bash
poetry install --all-groups
python -m codegen  # regenerate the client from spec/iiko-cloud-api.json
pytest
```

See [Development](https://tdeni.github.io/iikocloudapi/development/) for the code generator, tests and
releases.

## License

[MIT](https://github.com/tdeni/iikocloudapi/blob/master/LICENCE)
