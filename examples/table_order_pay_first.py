"""Pay first: a table order that reaches the restaurant already paid by an external acquirer.

The guest pays online (for example through T-Bank); once the payment is confirmed, the order is created with an
``External`` payment, so the cashier does not need to take money. The acquirer's payment ID is passed in
``paymentAdditionalData.customData``.

    IIKO_ORGANIZATION_ID=... IIKO_TERMINAL_GROUP_ID=... IIKO_TABLE_ID=... IIKO_PRODUCT_ID=... \\
    python -m examples.table_order_pay_first
"""

from __future__ import annotations

import asyncio
from decimal import Decimal

from iikocloudapi import IikoCloud
from iikocloudapi.models import (
    ExternalPayment,
    ExternalPaymentAdditionalData,
    PaymentType,
    ProductOrderItem,
    TableOrder,
)

try:
    from examples._env import client_from_env, env
except ImportError:  # pragma: no cover
    from _env import client_from_env, env  # type: ignore[no-redef]


async def external_payment_type(iiko: IikoCloud, organization_id: str) -> PaymentType:
    """The payment type configured in iikoOffice for payments processed outside of iiko."""
    response = await iiko.payment_types(organization_ids=[organization_id])
    for payment_type in response.payment_types:
        if payment_type.payment_type_kind == "External" and not payment_type.is_deleted:
            return payment_type
    msg = "No payment type of kind External; create one in iikoOffice"
    raise LookupError(msg)


async def main(
    iiko: IikoCloud,
    *,
    organization_id: str,
    terminal_group_id: str,
    table_id: str,
    product_id: str,
    price: Decimal,
    acquirer_payment_id: str,
) -> None:
    payment_type = await external_payment_type(iiko, organization_id)
    if payment_type.id is None:
        msg = "The payment type has no ID"
        raise LookupError(msg)

    created = await iiko.order.create(
        organization_id=organization_id,
        terminal_group_id=terminal_group_id,
        order=TableOrder(
            table_ids=[table_id],
            items=[ProductOrderItem(product_id=product_id, amount=Decimal(1), price=price)],
            payments=[
                ExternalPayment(
                    payment_type_id=payment_type.id,
                    sum=price,
                    is_processed_externally=True,
                    payment_additional_data=ExternalPaymentAdditionalData(custom_data=acquirer_payment_id),
                )
            ],
        ),
    )
    # Creating an order is a command: wait until the terminal has accepted it.
    await iiko.wait(created, organization_id=organization_id)

    found = await iiko.order.by_id(organization_ids=[organization_id], order_ids=[created.order_info.id])
    order = found.orders[0].order
    if order is not None:
        print(f"Order #{order.number}: {order.status}, {order.sum} paid {order.processed_payments_sum}")


if __name__ == "__main__":

    async def run() -> None:
        async with client_from_env() as iiko:
            await main(
                iiko,
                organization_id=env("IIKO_ORGANIZATION_ID"),
                terminal_group_id=env("IIKO_TERMINAL_GROUP_ID"),
                table_id=env("IIKO_TABLE_ID"),
                product_id=env("IIKO_PRODUCT_ID"),
                price=Decimal("450.00"),
                acquirer_payment_id="tbank-payment-id",
            )

    asyncio.run(run())
