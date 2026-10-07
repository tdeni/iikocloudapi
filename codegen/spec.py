"""Fetching, storing and walking the iikoCloud OpenAPI specification."""

from __future__ import annotations

import json
import re
import urllib.request
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from codegen.naming import safe_attr, snake

SPEC_URL = "https://api-ru.iiko.services/api-docs/docs"
DOCS_URL = "https://api-ru.iiko.services/docs"
ROOT = Path(__file__).resolve().parent.parent
SPEC_PATH = ROOT / "spec" / "iiko-cloud-api.json"

_VERSION_SEGMENT = re.compile(r"^v?\d+$")
# Attributes of ``IikoCloud`` that a top-level resource must not shadow.
RESERVED_ROOT_NAMES = frozenset({"auth", "base_url", "timeout", "request", "wait", "aclose"})
_COMMAND_MARKER = "This method is a command"

Schema = dict[str, Any]


def fetch(url: str = SPEC_URL) -> Schema:
    request = urllib.request.Request(url, headers={"User-Agent": "iikocloudapi-codegen"})  # noqa: S310
    with urllib.request.urlopen(request, timeout=60) as response:  # noqa: S310
        return json.load(response)


def load(path: Path = SPEC_PATH) -> Schema:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(spec: Schema) -> str:
    """Serialise the spec in a stable, diff-friendly form."""
    return json.dumps(spec, indent=1, ensure_ascii=False) + "\n"


def method_path(url: str) -> tuple[str, ...]:
    """Map an endpoint URL to the attribute path of the generated client method.

    ``/api/1/order/create`` -> ``("order", "create")``,
    ``/api/1/loyalty/iiko/customer/info`` -> ``("loyalty", "customer", "info")``.
    """
    segments = [s for s in url.split("/")[2:] if s and not _VERSION_SEGMENT.match(s)]
    if segments[:2] == ["loyalty", "iiko"]:
        segments = ["loyalty", *segments[2:]]
    path = [safe_attr(snake(s)) for s in segments]
    if path[0] in RESERVED_ROOT_NAMES:
        path[0] += "_"
    return tuple(path)


@dataclass
class Operation:
    url: str
    path: tuple[str, ...]
    tags: list[str]
    group: str
    summary: str
    description: str
    deprecated: bool
    request: Schema | None
    response: Schema | None
    status: int
    is_command: bool
    raw: Schema = field(repr=False)

    @property
    def tag(self) -> str:
        return self.tags[0]

    @property
    def docs_url(self) -> str:
        escaped = self.url.replace("~", "~0").replace("/", "~1")
        return f"{DOCS_URL}#tag/{self.tag.replace(' ', '-')}/paths/{escaped}/post"


@dataclass
class Webhook:
    name: str
    summary: str
    description: str
    schema_key: str


class Spec:
    def __init__(self, raw: Schema) -> None:
        self.raw = raw
        self.schemas: dict[str, Schema] = raw["components"]["schemas"]
        self.tag_groups: dict[str, list[str]] = {g["name"]: g["tags"] for g in raw.get("x-tagGroups", [])}
        self._group_of_tag = {tag: group for group, tags in self.tag_groups.items() for tag in tags}
        self.tag_descriptions = {t["name"]: t.get("description") or "" for t in raw.get("tags", [])}

    @staticmethod
    def ref_key(ref: str) -> str:
        return ref.rsplit("/", 1)[-1]

    def resolve(self, schema: Schema) -> Schema:
        while "$ref" in schema:
            schema = self.schemas[self.ref_key(schema["$ref"])]
        return schema

    def group_of_tag(self, tag: str) -> str:
        """Tag group of a tag; tags missing from ``x-tagGroups`` fall back to the group named like their prefix."""
        if tag in self._group_of_tag:
            return self._group_of_tag[tag]
        prefix = tag.split(".", 1)[0]
        return prefix if prefix in self.tag_groups else "General"

    def iter_refs(self, schema: Any) -> Iterator[str]:
        """Yield component keys referenced anywhere inside ``schema`` (not following them)."""
        if isinstance(schema, dict):
            if "$ref" in schema:
                yield self.ref_key(schema["$ref"])
            disc = schema.get("discriminator")
            if isinstance(disc, dict):
                for ref in disc.get("mapping", {}).values():
                    yield self.ref_key(ref)
            for key, value in schema.items():
                if key == "properties" and isinstance(value, dict):
                    for prop in value.values():  # property names may be anything, even "example"
                        yield from self.iter_refs(prop)
                elif key not in ("$ref", "discriminator", "example", "examples"):
                    yield from self.iter_refs(value)
        elif isinstance(schema, list):
            for item in schema:
                yield from self.iter_refs(item)

    def closure(self, roots: list[Schema]) -> set[str]:
        """All component keys transitively reachable from ``roots``."""
        seen: set[str] = set()
        stack = [ref for root in roots for ref in self.iter_refs(root)]
        while stack:
            key = stack.pop()
            if key in seen:
                continue
            seen.add(key)
            stack.extend(self.iter_refs(self.schemas[key]))
        return seen

    def _all_operations(self) -> list[Operation]:
        ops = []
        for url, item in self.raw["paths"].items():
            op = item.get("post")
            if op is None:  # the only GET is a deprecated duplicate of a POST endpoint
                continue
            request = op.get("requestBody", {}).get("content", {}).get("application/json", {}).get("schema")
            status, response = 200, None
            for code, resp in op.get("responses", {}).items():
                if code.startswith("2"):
                    status = int(code)
                    response = resp.get("content", {}).get("application/json", {}).get("schema")
                    break
            tags = op.get("tags") or ["Other"]
            description = op.get("description") or ""
            ops.append(
                Operation(
                    url=url,
                    path=method_path(url),
                    tags=tags,
                    group=self.group_of_tag(tags[0]),
                    summary=(op.get("summary") or "").strip(),
                    description=description,
                    deprecated=bool(op.get("deprecated")),
                    request=request,
                    response=response,
                    status=status,
                    is_command=_COMMAND_MARKER in description,
                    raw=op,
                )
            )
        return ops

    def operations(self) -> list[Operation]:
        """Operations exposed by the client.

        Deprecated endpoints are kept only when no live endpoint maps to the same method name.
        """
        by_path: dict[tuple[str, ...], list[Operation]] = {}
        for op in self._all_operations():
            by_path.setdefault(op.path, []).append(op)
        result = []
        for path, ops in by_path.items():
            live = [op for op in ops if not op.deprecated]
            chosen = live or ops
            if len(chosen) > 1:
                msg = f"Several endpoints map to {'.'.join(path)}: {[op.url for op in chosen]}"
                raise ValueError(msg)
            result.append(chosen[0])
        return sorted(result, key=lambda op: op.path)

    def dropped_operations(self) -> list[str]:
        kept = {op.url for op in self.operations()}
        return sorted({op.url for op in self._all_operations()} - kept)

    def webhooks(self) -> list[Webhook]:
        hooks = []
        for key, item in self.raw.get("x-webhooks", {}).items():
            op = item["post"]
            body = op["requestBody"]["content"]["application/json"]["schema"]
            schema_key = self.ref_key(body.get("items", body)["$ref"])
            hooks.append(
                Webhook(
                    name=key.rsplit(".", 1)[-1],
                    summary=(op.get("summary") or "").strip(),
                    description=op.get("description") or "",
                    schema_key=schema_key,
                )
            )
        return hooks
