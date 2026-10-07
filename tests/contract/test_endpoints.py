"""Contract tests: every generated method against the specification it was generated from."""

from __future__ import annotations

import json
from enum import Enum
from typing import Any

import jsonschema
import pytest
from pydantic import BaseModel

from codegen.spec import Operation, Spec
from iikocloudapi import IikoCloud, OpenIntEnum, OpenStrEnum
from tests.contract.synth import Synthesizer, json_schema, operations, spec
from tests.mock import FakeIiko

pytestmark = [pytest.mark.anyio, pytest.mark.filterwarnings("ignore:.*is deprecated by iikoCloud:DeprecationWarning")]

VARIANTS = 5  # enough to hit every member of the largest tagged union


def method_of(iiko: IikoCloud, op: Operation) -> Any:
    target: Any = iiko
    for segment in op.path:
        target = getattr(target, segment)
    return target


def leftovers(value: Any, path: str = "") -> list[str]:
    """Parts of a parsed response that the models did not understand.

    Fields that ended up in ``model_extra``, enum values that became pseudo-members and union members that fell
    back to the base model all mean that the generated models disagree with the specification.
    """
    found = []
    if isinstance(value, OpenStrEnum | OpenIntEnum) and not value.is_known:
        found.append(f"{path}: unknown enum value {value!r}")
    if isinstance(value, BaseModel):
        variants = type(value).__dict__.get("__variants__")
        if variants:
            tag = getattr(value, variants[0])
            if str(tag.value if isinstance(tag, Enum) else tag) not in variants[1]:
                found.append(f"{path}: fell back to {type(value).__name__}")
        found += [f"{path}.{name}" for name in (value.model_extra or {})]
        for name in type(value).model_fields:
            found += leftovers(getattr(value, name), f"{path}.{name}")
    elif isinstance(value, list):
        for i, item in enumerate(value):
            found += leftovers(item, f"{path}[{i}]")
    elif isinstance(value, dict):
        for k, item in value.items():
            found += leftovers(item, f"{path}[{k!r}]")
    return found


def request_kwargs(op: Operation, body: Any) -> dict[str, Any]:
    """Turn a JSON request body into keyword arguments of the generated method."""
    s = spec()
    if "$ref" not in (op.request or {}):
        return {"body": body}
    schema = s.schemas[Spec.ref_key(op.request["$ref"])]  # type: ignore[index]
    if isinstance(schema.get("discriminator"), dict):
        return {"body": body}
    from codegen.naming import field_name  # noqa: PLC0415

    return {field_name(alias): value for alias, value in body.items()}


def ids(op: Operation) -> str:
    return op.url


@pytest.mark.parametrize("op", [op for op in operations() if op.response], ids=ids)
async def test_response_is_fully_parsed(op: Operation) -> None:
    for variant in range(VARIANTS):
        for full in (True, False):
            body = Synthesizer(full=full, variant=variant).value(op.response)
            fake = FakeIiko(routes={op.url: body})
            async with fake.client() as iiko:
                kwargs = request_kwargs(op, Synthesizer(full=False).value(op.request)) if op.request else {}
                result = await method_of(iiko, op)(**kwargs)
            assert result is not None
            assert leftovers(result) == [], f"fields missing from the models (variant {variant}, full={full})"


@pytest.mark.parametrize("op", [op for op in operations() if op.request], ids=ids)
async def test_request_body_matches_spec(op: Operation) -> None:
    validator = jsonschema.Draft202012Validator(json_schema(op.request))  # type: ignore[arg-type]
    for variant in range(VARIANTS):
        for full in (True, False):
            body = Synthesizer(full=full, variant=variant).value(op.request)
            fake = FakeIiko(routes={op.url: Synthesizer(full=False).value(op.response) if op.response else {}})
            async with fake.client() as iiko:
                await method_of(iiko, op)(**request_kwargs(op, body))
            sent = [r for r in fake.requests if r.path == op.url][-1]
            assert sent.body == json.loads(json.dumps(body)), f"body round trip (variant {variant}, full={full})"
            errors = sorted(validator.iter_errors(sent.body), key=lambda e: list(e.absolute_path))
            assert not errors, "\n".join(f"{list(e.absolute_path)}: {e.message}" for e in errors[:5])


async def test_every_endpoint_is_covered() -> None:
    async with FakeIiko().client() as iiko:
        for op in operations():
            assert callable(method_of(iiko, op)), op.url
    assert len(operations()) > 300
