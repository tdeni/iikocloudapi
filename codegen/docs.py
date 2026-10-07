"""Generated documentation: API reference pages, the coverage table and the README coverage block."""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

from codegen.build import IR, MethodDef
from codegen.render import first_sentence, resource_tree
from codegen.spec import DOCS_URL

README_START = "<!-- coverage:start -->"
README_END = "<!-- coverage:end -->"
NAV_START = "# reference:start"
NAV_END = "# reference:end"


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def _pascal(segment: str) -> str:
    return "".join(p[:1].upper() + p[1:] for p in segment.split("_"))


def _qualname(method: MethodDef, calls: set[tuple[str, ...]]) -> str:
    """Dotted path of the generated method, as used by mkdocstrings."""
    path = method.op.path
    if path in calls:
        cls = "".join(_pascal(p) for p in path) + "Resource"
        return f"iikocloudapi.resources.{path[0]}.{cls}.__call__"
    if len(path) == 1:
        return f"iikocloudapi.resources.IikoCloudResources.{path[0]}"
    cls = "".join(_pascal(p) for p in path[:-1]) + "Resource"
    return f"iikocloudapi.resources.{path[0]}.{cls}.{path[-1]}"


def _call(method: MethodDef) -> str:
    return "iiko." + ".".join(method.op.path) + "()"


def _groups(ir: IR) -> dict[str, dict[str, list[MethodDef]]]:
    """x-tagGroups -> tag -> methods, in the order used by the official documentation."""
    by_tag: dict[str, list[MethodDef]] = defaultdict(list)
    for method in ir.methods:
        by_tag[method.op.tag].append(method)
    result: dict[str, dict[str, list[MethodDef]]] = {}
    for group, tags in ir.spec.tag_groups.items():
        section = {tag: by_tag.pop(tag) for tag in tags if tag in by_tag}
        if section:
            result[group] = section
    for tag in sorted(by_tag):
        result.setdefault(ir.spec.group_of_tag(tag), {})[tag] = by_tag[tag]
    return result


def _group_page(group: str) -> str:
    return f"reference/{_slug(group)}.md"


def render_group(group: str, tags: dict[str, list[MethodDef]], ir: IR, calls: set[tuple[str, ...]]) -> str:
    lines = [f"# {group}", ""]
    lines.append(f"Endpoints of the *{group}* section of the [iikoCloud API documentation]({DOCS_URL}).")
    lines.append("")
    for tag, methods in tags.items():
        lines += [f"## {tag}", ""]
        description = ir.spec.tag_descriptions.get(tag, "").strip()
        if description:
            lines += [first_sentence(re.sub(r"<[^>]+>", " ", description)), ""]
        for method in methods:
            lines += [
                f"::: {_qualname(method, calls)}",
                "    options:",
                f'      heading: "{_call(method)}"',
                f'      toc_label: "{".".join(method.op.path)}"',
                "      heading_level: 3",
                "      show_root_heading: true",
                "      show_root_full_path: false",
                "",
            ]
    return "\n".join(lines)


def render_models_page(module: str) -> str:
    title = "Common models" if module == "common" else f"{module.title()} models"
    return "\n".join(
        [
            f"# {title}",
            "",
            f"::: iikocloudapi.models.{module}",
            "    options:",
            "      show_root_heading: false",
            "      members_order: alphabetical",
            "      heading_level: 2",
            "      show_bases: true",
            "      show_signature: false",
            "      filters: ['!^_', '!^model_']",
            "",
        ]
    )


def render_index(groups: dict[str, dict[str, list[MethodDef]]], ir: IR, calls: set[tuple[str, ...]]) -> str:
    total = sum(len(ms) for tags in groups.values() for ms in tags.values())
    lines = [
        "# API coverage",
        "",
        f"All **{total}** endpoints of the [iikoCloud API]({DOCS_URL}) that are not superseded by a newer version.",
        "The attribute path of each method mirrors the endpoint URL. *Commands* return a `correlation_id`;",
        "see [Asynchronous commands](../guide/commands.md).",
        "",
    ]
    dropped = ir.spec.dropped_operations()
    if dropped:
        lines += [
            "Deprecated endpoints replaced by a newer version are not exposed: "
            + ", ".join(f"`{url}`" for url in dropped)
            + ". `/api/1/access_token` is still supported through `ApiLoginAuth`.",
            "",
        ]
    for group, tags in groups.items():
        page = _group_page(group).removeprefix("reference/")
        lines += [f"## [{group}]({page})", ""]
        lines += ["| Endpoint | Method | Description |", "| --- | --- | --- |"]
        for methods in tags.values():
            for method in methods:
                anchor = _qualname(method, calls)
                flags = " *(deprecated)*" if method.op.deprecated else ""
                flags += " *(command)*" if method.op.is_command else ""
                summary = method.op.summary.replace("\n", " ").replace("|", "\\|").rstrip(".")
                lines.append(f"| `{method.op.url}` | [`{_call(method)}`]({page}#{anchor}) | {summary}{flags} |")
        lines.append("")
    return "\n".join(lines)


def render_client_page() -> str:
    return """# Client

::: iikocloudapi.IikoCloud
    options:
      members: [request, wait, aclose]
      show_root_heading: true
      heading_level: 2

## Authentication

::: iikocloudapi.AppAuth
    options:
      heading_level: 3
      show_root_heading: true

::: iikocloudapi.ApiLoginAuth
    options:
      heading_level: 3
      show_root_heading: true

::: iikocloudapi.IikoAuth
    options:
      heading_level: 3
      show_root_heading: true
      members: [token_request, parse_token_response, token, invalidate]

## Errors

::: iikocloudapi._errors
    options:
      show_root_heading: false
      heading_level: 3
      members_order: source
      filters: ['!^_', '!^error_from_response$']

## Webhooks

::: iikocloudapi.webhooks
    options:
      show_root_heading: false
      heading_level: 3
      members: [parse_webhook, verify_webhook_token]

## Types

::: iikocloudapi._base
    options:
      show_root_heading: false
      heading_level: 3
      members: [IikoModel, OpenStrEnum, OpenIntEnum, IikoDateTime, IsoDateTime, OrganizationItems]
"""


def render_readme_block(groups: dict[str, dict[str, list[MethodDef]]]) -> str:
    total = sum(len(ms) for tags in groups.values() for ms in tags.values())
    lines = [
        README_START,
        "",
        f"**{total} endpoints**: every iikoCloud API endpoint that is not superseded by a newer version.",
        "",
        "| Section | Endpoints |",
        "| --- | ---: |",
    ]
    lines += [f"| {group} | {sum(len(ms) for ms in tags.values())} |" for group, tags in groups.items()]
    lines.append("")
    for group, tags in groups.items():
        lines += [f"<details><summary><b>{group}</b></summary>", "", "| Endpoint | Method |", "| --- | --- |"]
        for methods in tags.values():
            lines += [f"| `{m.op.url}` | `{_call(m)}` |" for m in methods]
        lines += ["", "</details>", ""]
    lines.append(README_END)
    return "\n".join(lines)


def _replace_between(text: str, start: str, end: str, block: str) -> str:
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
    return pattern.sub(lambda _: block, text, count=1)


def render_nav(groups: dict[str, dict[str, list[MethodDef]]], modules: list[str]) -> str:
    pad = "      "
    lines = [
        NAV_START,
        f"{pad}- Coverage: reference/index.md",
        f"{pad}- Client: reference/client.md",
        f"{pad}- Endpoints:",
    ]
    lines += [f"{pad}    - {group}: {_group_page(group)}" for group in groups]
    lines.append(f"{pad}- Models:")
    lines += [f"{pad}    - {m.title()}: reference/models/{m}.md" for m in modules]
    lines.append(f"{pad[:-2]}{NAV_END}")
    return "\n".join(lines)


def render_docs(ir: IR, root: Path) -> dict[str, str]:
    tree = resource_tree(ir.methods)
    calls = {node.call.op.path for node in tree.walk() if node.call}
    groups = _groups(ir)
    files: dict[str, str] = {}
    for group, tags in groups.items():
        files[f"docs/{_group_page(group)}"] = render_group(group, tags, ir, calls)
    for module in ir.modules:
        files[f"docs/reference/models/{module}.md"] = render_models_page(module)
    files["docs/reference/index.md"] = render_index(groups, ir, calls)
    files["docs/reference/client.md"] = render_client_page()

    readme = root / "README.md"
    if readme.exists():
        text = readme.read_text(encoding="utf-8")
        files["README.md"] = _replace_between(text, README_START, README_END, render_readme_block(groups))
    mkdocs = root / "mkdocs.yml"
    if mkdocs.exists():
        text = mkdocs.read_text(encoding="utf-8")
        files["mkdocs.yml"] = _replace_between(text, NAV_START, NAV_END, render_nav(groups, ir.modules))
    return files
