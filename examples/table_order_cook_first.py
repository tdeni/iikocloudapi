"""Cook first: open a table order, add dishes while the guest is eating, then pay with held funds and close it.

1. The guest scans the QR code on the table. If the table already has an open order, dishes are added to it
   instead of creating a second order.
2. When the guest asks for the bill, the acquirer confirms the funds held on the card.
3. The external payment is attached to the order and the order is closed.

Every step that changes the order is a command, so each one is followed by ``iiko.wait()``.

    IIKO_ORGANIZATION_ID=... IIKO_TERMINAL_GROUP_ID=... IIKO_TABLE_ID=... IIKO_PRODUCT_ID=... \\
    IIKO_PAYMENT_TYPE_ID=... python -m examples.table_order_cook_first
"""

from __future__ import annotations

import asyncio
from decimal import Decimal

from iikocloudapi import IikoCloud
from iikocloudapi.models import (
    ExternalPayment,
    ExternalPaymentAdditionalData,
    OrderItem,
    OrderStatus,
    ProductOrderItem,
    TableOrder,
)

try:
    from examples._env import client_from_env, env
except ImportError:  # pragma: no cover
    from _env import client_from_env, env  # type: ignore[no-redef]


async def open_order_on_table(iiko: IikoCloud, organization_id: str, table_id: str) -> str | None:
    """ID of an order that is still open on the table, if any."""
    found = await iiko.order.by_table(
        organization_ids=[organization_id],
        table_ids=[table_id],
        statuses=[OrderStatus.NEW, OrderStatus.BILL],
    )
    return found.orders[0].id if found.orders else None


async def add_dishes(
    iiko: IikoCloud, *, organization_id: str, terminal_group_id: str, table_id: str, items: list[OrderItem]
) -> str:
    order_id = await open_order_on_table(iiko, organization_id, table_id)
    if order_id is None:
        created = await iiko.order.create(
            organization_id=organization_id,
            terminal_group_id=terminal_group_id,
            order=TableOrder(table_ids=[table_id], items=items),
        )
        await iiko.wait(created, organization_id=organization_id)
        return created.order_info.id
    added = await iiko.order.add_items(organization_id=organization_id, order_id=order_id, items=items)
    await iiko.wait(added, organization_id=organization_id)
    return order_id


async def pay_and_close(
    iiko: IikoCloud, *, organization_id: str, order_id: str, payment_type_id: str, acquirer_payment_id: str
) -> None:
    found = await iiko.order.by_id(organization_ids=[organization_id], order_ids=[order_id])
    order = found.orders[0].order
    if order is None:
        msg = f"Order {order_id} is not available yet"
        raise LookupError(msg)

    paid = await iiko.order.change_payments(
        organization_id=organization_id,
        order_id=order_id,
        payments=[
            ExternalPayment(
                payment_type_id=payment_type_id,
                sum=order.sum,
                is_processed_externally=True,
                payment_additional_data=ExternalPaymentAdditionalData(custom_data=acquirer_payment_id),
            )
        ],
    )
    await iiko.wait(paid, organization_id=organization_id)

    closed = await iiko.order.close(organization_id=organization_id, order_id=order_id)
    await iiko.wait(closed, organization_id=organization_id)
    print(f"Order #{order.number} paid ({order.sum}) and closed")


async def main(
    iiko: IikoCloud,
    *,
    organization_id: str,
    terminal_group_id: str,
    table_id: str,
    product_id: str,
    payment_type_id: str,
) -> None:
    dishes: list[OrderItem] = [ProductOrderItem(product_id=product_id, amount=Decimal(2), price=Decimal("320.00"))]
    order_id = await add_dishes(
        iiko, organization_id=organization_id, terminal_group_id=terminal_group_id, table_id=table_id, items=dishes
    )
    # ... later, the acquirer confirms the funds held on the guest's card ...
    await pay_and_close(
        iiko,
        organization_id=organization_id,
        order_id=order_id,
        payment_type_id=payment_type_id,
        acquirer_payment_id="tbank-payment-id",
    )


if __name__ == "__main__":

    async def run() -> None:
        async with client_from_env() as iiko:
            await main(
                iiko,
                organization_id=env("IIKO_ORGANIZATION_ID"),
                terminal_group_id=env("IIKO_TERMINAL_GROUP_ID"),
                table_id=env("IIKO_TABLE_ID"),
                product_id=env("IIKO_PRODUCT_ID"),
                payment_type_id=env("IIKO_PAYMENT_TYPE_ID"),
            )

    asyncio.run(run())
