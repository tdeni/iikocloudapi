from __future__ import annotations

import pytest

from tests.mock import FakeIiko


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def fake() -> FakeIiko:
    return FakeIiko()
