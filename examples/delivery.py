"""Create a delivery order paid in cash on delivery and follow its status.

The address format depends on the organization's ``addressFormatType`` setting: ``AddressCity`` takes a free-form
line, ``AddressLegacy`` needs a street from ``iiko.streets.by_city()``.

    IIKO_ORGANIZATION_ID=... IIKO_TERMINAL_GROUP_ID=... IIKO_PRODUCT_ID=... IIKO_PAYMENT_TYPE_ID=... \\
    python -m examples.delivery
"""

from __future__ import annotations

import asyncio
from decimal import Decimal

from iikocloudapi import CommandFailed, IikoCloud
from iikocloudapi.models import (
    AddressCity,
    CashPayment,
    DeliveryOrder,
    DeliveryPoint,
    DeliveryServiceType,
    ProductOrderItem,
    RegularCustomer,
)

try:
    from examples._env import client_from_env, env
except ImportError:  # pragma: no cover
    from _env import client_from_env, env  # type: ignore[no-redef]


async def main(
    iiko: IikoCloud,
    *,
    organization_id: str,
    terminal_group_id: str,
    product_id: str,
    cash_payment_type_id: str,
) -> None:
    price = Decimal("390.00")
    order = DeliveryOrder(
        phone="+79990000000",
        order_service_type=DeliveryServiceType.DELIVERY_BY_COURIER,
        customer=RegularCustomer(name="Anna"),
        delivery_point=DeliveryPoint(
            address=AddressCity(line1="Moscow, Tverskaya st. 1", flat="12", floor="3"),
            comment="Entrance from the yard",
        ),
        items=[ProductOrderItem(product_id=product_id, amount=Decimal(2), price=price)],
        payments=[CashPayment(payment_type_id=cash_payment_type_id, sum=price * 2)],
        comment="Please call 10 minutes before arrival",
    )
    created = await iiko.deliveries.create(
        organization_id=organization_id, terminal_group_id=terminal_group_id, order=order
    )
    try:
        await iiko.wait(created, organization_id=organization_id)
    except CommandFailed as error:
        print(f"The terminal rejected the order: {error}")
        return

    found = await iiko.deliveries.by_id(organization_id=organization_id, order_ids=[created.order_info.id])
    delivery = found.orders[0].order
    if delivery is not None:
        print(f"Delivery #{delivery.number}: {delivery.status}, complete before {delivery.complete_before}")


if __name__ == "__main__":

    async def run() -> None:
        async with client_from_env() as iiko:
            await main(
                iiko,
                organization_id=env("IIKO_ORGANIZATION_ID"),
                terminal_group_id=env("IIKO_TERMINAL_GROUP_ID"),
                product_id=env("IIKO_PRODUCT_ID"),
                cash_payment_type_id=env("IIKO_PAYMENT_TYPE_ID"),
            )

    asyncio.run(run())
