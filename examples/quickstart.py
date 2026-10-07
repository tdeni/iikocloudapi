"""List organizations and their terminal groups, and check that the terminals are online.

python -m examples.quickstart
"""

from __future__ import annotations

import asyncio

from iikocloudapi import IikoCloud

try:
    from examples._env import client_from_env
except ImportError:  # pragma: no cover - when run as a script from the examples directory
    from _env import client_from_env  # type: ignore[no-redef]


async def main(iiko: IikoCloud) -> None:
    organizations = await iiko.organizations()
    organization_ids = [org.id for org in organizations.organizations]

    groups = await iiko.terminal_groups(organization_ids=organization_ids)
    terminal_groups = [group for org in groups.terminal_groups for group in org.items]

    alive = await iiko.terminal_groups.is_alive(
        organization_ids=organization_ids,
        terminal_group_ids=[group.id for group in terminal_groups],
    )
    online = {status.terminal_group_id: status.is_alive for status in alive.is_alive_status}

    for org in organizations.organizations:
        print(f"{org.name} ({org.id})")
        for group in terminal_groups:
            if group.organization_id == org.id:
                state = "online" if online.get(group.id) else "offline"
                print(f"  {group.name}: {state}, time zone {group.time_zone}")


if __name__ == "__main__":

    async def run() -> None:
        async with client_from_env() as iiko:
            await main(iiko)

    asyncio.run(run())
