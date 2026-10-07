"""Shared helpers: build a client from environment variables.

``AppAuth`` reads ``IIKO_API_KEY``, ``IIKO_APP_ID`` and ``IIKO_CLIENT_SECRET``. If ``IIKO_API_LOGIN`` is set, the
legacy ``ApiLoginAuth`` is used instead. ``IIKO_BASE_URL`` defaults to https://api-ru.iiko.services.
"""

from __future__ import annotations

import os

from iikocloudapi import API_RU, ApiLoginAuth, AppAuth, IikoCloud


def client_from_env() -> IikoCloud:
    api_login = os.environ.get("IIKO_API_LOGIN")
    if api_login:
        auth: AppAuth | ApiLoginAuth = ApiLoginAuth(api_login)
    else:
        auth = AppAuth(
            api_key=os.environ["IIKO_API_KEY"],
            app_id=os.environ["IIKO_APP_ID"],
            client_secret=os.environ["IIKO_CLIENT_SECRET"],
        )
    return IikoCloud(auth=auth, base_url=os.environ.get("IIKO_BASE_URL", API_RU))


def env(name: str) -> str:
    """A required setting for an example."""
    value = os.environ.get(name)
    if not value:
        raise SystemExit(f"Set the {name} environment variable to run this example.")
    return value
