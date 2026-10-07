"""Synthesise JSON documents from the specification and convert its schemas to JSON Schema.

The contract tests use these helpers to check every generated method against the specification it was generated
from: synthesised responses must parse without leftovers, and request bodies built by the client must validate.
"""

from __future__ import annotations

import re
from functools import cache
from typing import Any

from codegen.spec import Operation, Spec, load

_CONSTANT = re.compile(r"^constant string '(.*)'$")
UUID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
MAX_DEPTH = 7


@cache
def spec() -> Spec:
    return Spec(load())


@cache
def operations() -> list[Operation]:
    return spec().operations()


@cache
def literal_tags() -> dict[str, tuple[str, str]]:
    """Mapping target schema key -> (discriminator property, tag)."""
    tags: dict[str, tuple[str, str]] = {}
    for schema in spec().schemas.values():
        disc = schema.get("discriminator")
        if isinstance(disc, dict):
            for tag, ref in disc.get("mapping", {}).items():
                tags.setdefault(Spec.ref_key(ref), (disc["propertyName"], tag))
    return tags


def _merged(schema: dict[str, Any]) -> tuple[dict[str, Any], set[str]]:
    """Properties and required names of an object schema, following ``allOf``."""
    s = spec()
    props: dict[str, Any] = {}
    required = set(schema.get("required", []))
    for part in schema.get("allOf", []):
        p, r = _merged(s.resolve(part))
        props.update(p)
        required |= r
    props.update(schema.get("properties", {}))
    return props, required


class Synthesizer:
    """Build a JSON value that satisfies a schema.

    Args:
        full: Fill every property (``True``) or only the required ones (``False``).
        variant: Index used to pick union variants and enum values, so that several runs cover all of them.
    """

    def __init__(self, *, full: bool, variant: int = 0) -> None:
        self.full = full
        self.variant = variant

    def value(self, schema: dict[str, Any] | None, depth: int = 0, stack: tuple[str, ...] = ()) -> Any:  # noqa: PLR0911
        if not schema:
            return "any"
        if "$ref" in schema:
            key = Spec.ref_key(schema["$ref"])
            return self.component(key, depth, stack)
        if "allOf" in schema and len(schema["allOf"]) == 1 and "properties" not in schema:
            return self.value(schema["allOf"][0], depth, stack)
        if "oneOf" in schema:
            options = schema["oneOf"]
            return self.value(options[self.variant % len(options)], depth, stack)
        kind = schema.get("type")
        if isinstance(kind, str) and (match := _CONSTANT.match(kind)):
            return match.group(1)
        if "enum" in schema:
            return schema["enum"][self.variant % len(schema["enum"])]
        if kind == "array":
            if depth >= MAX_DEPTH:
                return []
            return [self.value(schema.get("items"), depth + 1, stack)]
        if kind == "Array of strings <uuid>":
            return [UUID]
        if kind == "object" or "properties" in schema or "allOf" in schema:
            return self.obj(schema, depth, stack, None)
        fmt = schema.get("format")
        if kind in ("string", "uuid"):
            if fmt == "uuid" or kind == "uuid":
                return UUID
            if fmt == "yyyy-MM-dd HH:mm:ss.fff":
                return "2024-01-02 03:04:05.678"
            if fmt == "date-time":
                return "2024-01-02T03:04:05+00:00"
            if fmt == "date":
                return "2024-01-02"
            if fmt == "date-span":
                return "01:30:00"
            length = max(schema.get("minLength", 0), min(6, schema.get("maxLength", 6)))
            return "string"[:length].ljust(length, "x")
        if kind in ("integer", "int", "integer <int32>", "integer <int64>"):
            return max(1, schema.get("minimum", 1)) if "maximum" not in schema else schema["maximum"]
        if kind in ("number", "float"):
            return 1.5
        if kind in ("boolean", "bool"):
            return True
        if kind == "enum":
            return "string"
        return "any"

    def component(self, key: str, depth: int, stack: tuple[str, ...]) -> Any:
        s = spec()
        schema = s.schemas[key]
        disc = schema.get("discriminator")
        if isinstance(disc, dict) and disc.get("mapping"):
            refs = list(disc["mapping"].values())
            target = Spec.ref_key(refs[self.variant % len(refs)])
            if target != key:
                return self.component(target, depth, stack)
        if "enum" in schema:
            return schema["enum"][self.variant % len(schema["enum"])]
        return self.obj(schema, depth, (*stack, key), key)

    def obj(self, schema: dict[str, Any], depth: int, stack: tuple[str, ...], key: str | None) -> Any:
        props, required = _merged(schema)
        result: dict[str, Any] = {}
        recursive = key is not None and stack.count(key) > 1
        for name, prop in props.items():
            if name not in required and (not self.full or recursive or depth >= MAX_DEPTH):
                continue
            result[name] = self.value(prop, depth + 1, stack)
        extra = schema.get("additionalProperties")
        if not props and isinstance(extra, dict) and extra and self.full and depth < MAX_DEPTH:
            result["key"] = self.value(extra, depth + 1, stack)
        if key in literal_tags():
            prop_name, tag = literal_tags()[key]
            result[prop_name] = tag
        return result


def _convert(schema: Any) -> Any:
    if isinstance(schema, list):
        return [_convert(item) for item in schema]
    if not isinstance(schema, dict):
        return schema
    if "$ref" in schema:
        key = Spec.ref_key(schema["$ref"])
        return {"$ref": f"#/$defs/{_escape(key)}"}
    out = {k: _convert(v) for k, v in schema.items() if k not in ("discriminator", "nullable", "example", "format")}
    kind = schema.get("type")
    if isinstance(kind, str):
        if match := _CONSTANT.match(kind):
            out.pop("type")
            out["const"] = match.group(1)
        elif kind == "float":
            out["type"] = "number"
        elif kind == "bool":
            out["type"] = "boolean"
        elif kind in ("int", "integer <int32>", "integer <int64>"):
            out["type"] = "integer"
        elif kind in ("uuid", "enum"):
            out["type"] = "string"
        elif kind == "Array of strings <uuid>":
            out["type"] = "array"
            out["items"] = {"type": "string"}
    if schema.get("nullable"):
        return {"anyOf": [out, {"type": "null"}]}
    return out


def _escape(key: str) -> str:
    return key.replace("~", "~0").replace("/", "~1")


@cache
def json_schema_defs() -> dict[str, Any]:
    """All components as JSON Schema ``$defs``: ``allOf`` is flattened, polymorphic bases become ``anyOf``."""
    s = spec()
    defs: dict[str, Any] = {}
    for key, schema in s.schemas.items():
        if "enum" in schema or ("properties" not in schema and "allOf" not in schema):
            defs[_escape(key)] = _convert(schema)
            continue
        props, required = _merged(schema)
        flat: dict[str, Any] = {
            "type": "object",
            "properties": {name: _convert(prop) for name, prop in props.items()},
            "required": sorted(required),
        }
        if schema.get("additionalProperties") is False or any(
            s.resolve(p).get("additionalProperties") is False for p in schema.get("allOf", [])
        ):
            flat["additionalProperties"] = False
        if key in literal_tags():
            prop_name, tag = literal_tags()[key]
            flat["properties"][prop_name] = {"const": tag}
        disc = schema.get("discriminator")
        if isinstance(disc, dict) and disc.get("mapping"):
            variants = [Spec.ref_key(ref) for ref in disc["mapping"].values()]
            defs[_escape(key) + "__union__"] = flat
            defs[_escape(key)] = {
                "anyOf": [
                    {"$ref": f"#/$defs/{_escape(v)}"} if v != key else {"$ref": f"#/$defs/{_escape(key)}__union__"}
                    for v in variants
                ]
            }
        else:
            defs[_escape(key)] = flat
    return defs


def json_schema(schema: dict[str, Any]) -> dict[str, Any]:
    return {"$defs": json_schema_defs(), **_convert(schema)}
