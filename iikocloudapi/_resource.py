"""Base class of the generated API resources."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from iikocloudapi._client import IikoCloud


class Resource:
    """A group of endpoints that share a URL prefix."""

    __slots__ = ("_client",)

    def __init__(self, client: IikoCloud) -> None:
        self._client = client
