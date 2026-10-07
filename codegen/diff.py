"""Human-readable summary of the differences between two versions of the specification."""

from __future__ import annotations

from codegen.spec import Spec


def _properties(spec: Spec, key: str) -> dict[str, tuple[str, bool]]:
    schema = spec.schemas[key]
    props: dict[str, tuple[str, bool]] = {}
    required = set(schema.get("required", []))
    parts = [schema, *[p for p in schema.get("allOf", []) if "$ref" not in p]]
    for part in parts:
        required |= set(part.get("required", []))
        for name, prop in part.get("properties", {}).items():
            kind = prop.get("type") or prop.get("$ref", "").rsplit(".", 1)[-1] or "object"
            props[name] = (str(kind), False)
    return {name: (kind, name in required) for name, (kind, _) in props.items()}


def summarize(old: Spec, new: Spec) -> str:
    old_ops = {op.url: op for op in old.operations()}
    new_ops = {op.url: op for op in new.operations()}
    lines: list[str] = []

    added = sorted(new_ops.keys() - old_ops.keys())
    removed = sorted(old_ops.keys() - new_ops.keys())
    deprecated = sorted(
        u for u in new_ops.keys() & old_ops.keys() if new_ops[u].deprecated and not old_ops[u].deprecated
    )
    if added:
        lines += ["### New endpoints", ""]
        lines += [f"- `{u}`: `iiko.{'.'.join(new_ops[u].path)}()`, {new_ops[u].summary}" for u in added]
        lines.append("")
    if removed:
        lines += ["### Removed endpoints", ""]
        lines += [f"- `{u}` (was `iiko.{'.'.join(old_ops[u].path)}()`)" for u in removed]
        lines.append("")
    if deprecated:
        lines += ["### Newly deprecated endpoints", ""]
        lines += [f"- `{u}`" for u in deprecated]
        lines.append("")

    changes: list[str] = []
    for key in sorted(old.schemas.keys() & new.schemas.keys()):
        before, after = _properties(old, key), _properties(new, key)
        if before == after and old.schemas[key].get("enum") == new.schemas[key].get("enum"):
            continue
        name = key.split("`", 1)[0].rsplit(".", 1)[-1]
        details = []
        details += [f"+`{p}`" for p in sorted(after.keys() - before.keys())]
        details += [f"-`{p}`" for p in sorted(before.keys() - after.keys())]
        for p in sorted(before.keys() & after.keys()):
            if before[p] != after[p]:
                details.append(
                    f"~`{p}` ({before[p][0]}{'*' if before[p][1] else ''} to {after[p][0]}{'*' if after[p][1] else ''})"
                )
        old_enum, new_enum = old.schemas[key].get("enum") or [], new.schemas[key].get("enum") or []
        details += [f"+{v!r}" for v in new_enum if v not in old_enum]
        details += [f"-{v!r}" for v in old_enum if v not in new_enum]
        if details:
            changes.append(f"- `{name}`: {', '.join(details)}")
    new_schemas = sorted(new.schemas.keys() - old.schemas.keys())
    if changes or new_schemas:
        lines += ["### Changed schemas", "", "`*` marks required fields.", ""]
        lines += changes
        if new_schemas:
            lines.append(
                f"- {len(new_schemas)} new schema(s): "
                + ", ".join(f"`{k.rsplit('.', 1)[-1]}`" for k in new_schemas[:30])
            )
        lines.append("")

    if not lines:
        return "No changes in the iikoCloud API specification."
    return "## iikoCloud API specification changes\n\n" + "\n".join(lines).rstrip()
