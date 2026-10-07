"""Download an external menu (v3) and mark the dishes that are in the stop list.

IIKO_ORGANIZATION_ID=... python -m examples.menu_sync
"""

from __future__ import annotations

import asyncio

from iikocloudapi import IikoCloud

try:
    from examples._env import client_from_env, env
except ImportError:  # pragma: no cover
    from _env import client_from_env, env  # type: ignore[no-redef]


async def out_of_stock(iiko: IikoCloud, organization_id: str) -> set[str]:
    """IDs of products that cannot be sold right now on any terminal group of the organization."""
    response = await iiko.stop_lists(organization_ids=[organization_id])
    return {
        item.product_id
        for organization in response.terminal_group_stop_lists
        for terminal_group in organization.items
        for item in terminal_group.items
        if item.balance <= 0
    }


async def main(iiko: IikoCloud, *, organization_id: str) -> None:
    menus = await iiko.menu()
    if not menus.external_menus:
        print("No external menus are configured in iikoWeb")
        return
    external_menu = menus.external_menus[0]
    price_category = menus.price_categories[0] if menus.price_categories else None

    menu = await iiko.menu.by_id(
        external_menu_id=external_menu.id,
        organization_id=organization_id,
        price_category_id=price_category.id if price_category else None,
    )
    stopped = await out_of_stock(iiko, organization_id)

    print(f"Menu {menu.name!r}")
    for group in menu.items_groups or []:
        print(f"  {group.name}")
        for item in group.items or []:
            prices = [p.price for p in item.size_prices or [] if p.price is not None]
            price = f"{min(prices)}" if prices else "no price"
            mark = " (stop list)" if item.product_id in stopped else ""
            print(f"    {item.name}: {price}{mark}")


if __name__ == "__main__":

    async def run() -> None:
        async with client_from_env() as iiko:
            await main(iiko, organization_id=env("IIKO_ORGANIZATION_ID"))

    asyncio.run(run())
