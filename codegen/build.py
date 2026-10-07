"""Turn the specification into an intermediate representation (models, enums, unions, methods)."""

from __future__ import annotations

import html
import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Literal

from codegen import overrides
from codegen.naming import field_name, needs_explicit_alias, pascal, safe_attr, singular, upper_snake
from codegen.spec import Operation, Schema, Spec, Webhook

WRAPPER = "RmsItemsResponseWrapper"
WRAPPER_CLASS = "OrganizationItems"
IIKO_DATETIME_FORMAT = "yyyy-MM-dd HH:mm:ss.fff"
COMMON = "common"
WEBHOOKS_GROUP = "WebHooks"

_CONSTANT_STRING = re.compile(r"^constant string '(.*)'$")
_INT_ENUM_ITEM = re.compile(r"(?:^|\n)\s*(-?\d+)\s*[-\u2013\u2014=:]\s*([^,;\n]+)")


@dataclass
class FieldDef:
    name: str
    alias: str
    annotation: str
    input_annotation: str
    required: bool
    description: str
    extras: dict[str, Any] = field(default_factory=dict)
    default: str | None = None
    override: bool = False
    always_send: bool = False

    @property
    def explicit_alias(self) -> bool:
        return needs_explicit_alias(self.name, self.alias)


@dataclass
class ModelDef:
    key: str
    name: str
    module: str
    base: str | None
    fields: list[FieldDef]
    description: str
    discriminators: list[str] = field(default_factory=list)
    deps: set[str] = field(default_factory=set)
    request_only: bool = False
    variants: tuple[str, tuple[str, ...]] | None = None


@dataclass
class EnumDef:
    key: str
    name: str
    module: str
    kind: Literal["str", "int"]
    members: list[tuple[str, Any, str]]
    description: str


@dataclass
class UnionDef:
    key: str
    name: str
    module: str
    discriminator_alias: str
    discriminator_name: str
    members: list[tuple[Any, str]]
    fallback: str
    description: str
    deps: set[str] = field(default_factory=set)


@dataclass
class MethodDef:
    op: Operation
    name: str
    params: list[FieldDef]
    request_model: str | None
    body_param: FieldDef | None
    response: str
    response_runtime: str
    deps: set[str] = field(default_factory=set)


@dataclass
class IR:
    spec: Spec
    models: dict[str, ModelDef]
    enums: dict[str, EnumDef]
    unions: dict[str, UnionDef]
    methods: list[MethodDef]
    webhooks: list[Webhook]
    webhook_union: UnionDef
    module_of: dict[str, str]

    def module_items(self, module: str) -> tuple[list[EnumDef], list[ModelDef], list[UnionDef]]:
        enums = sorted((e for e in self.enums.values() if e.module == module), key=lambda e: e.name)
        models = [m for m in self.models.values() if m.module == module]
        unions = sorted((u for u in self.unions.values() if u.module == module), key=lambda u: u.name)
        if self.webhook_union.module == module:
            unions.append(self.webhook_union)
        return enums, _topological(models), unions

    @property
    def modules(self) -> list[str]:
        return sorted(set(self.module_of.values()))


def _topological(models: list[ModelDef]) -> list[ModelDef]:
    """Order models so that every base class comes before its subclasses (stable by name otherwise)."""
    by_name = {m.name: m for m in models}
    ordered: list[ModelDef] = []
    done: set[str] = set()

    def visit(model: ModelDef) -> None:
        if model.name in done:
            return
        done.add(model.name)
        if model.base in by_name:
            visit(by_name[model.base])
        ordered.append(model)

    for model in sorted(models, key=lambda m: m.name):
        visit(model)
    return ordered


_TAGS = [
    (re.compile(r"</?br\s*/?>", re.IGNORECASE), "\n"),
    (re.compile(r"</?remarks>", re.IGNORECASE), "\n"),
    (re.compile(r"</?(b|strong)>", re.IGNORECASE), "**"),
    (re.compile(r"</?(i|em)>", re.IGNORECASE), "*"),
    (re.compile(r"</?code>", re.IGNORECASE), "`"),
    (re.compile(r"<li>", re.IGNORECASE), "\n- "),
    (re.compile(r"</?(p|ul|ol|li|h\d|div|span)[^>]*>", re.IGNORECASE), "\n"),
]


def clean_text(text: str | None) -> str:
    """Normalise the HTML/markdown mix used in spec descriptions into plain markdown."""
    if not text:
        return ""
    for pattern, repl in _TAGS:
        text = pattern.sub(repl, text)
    text = html.unescape(text)
    lines = [line.rstrip() for line in text.replace("\r", "").split("\n")]
    lines = [re.sub(r"^\s*>\s?", "", line) for line in lines]
    lines = [line.strip() for line in lines]
    text = "\n".join(lines)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def _short(key: str) -> str:
    return key.split("`", 1)[0].rsplit(".", 1)[-1]


def _namespace(key: str) -> str:
    base = key.split("`", 1)[0]
    return base.rsplit(".", 1)[0] if "." in base else ""


def _priority(namespace: str) -> int:
    segments = namespace.split(".")
    if "Request" in segments:
        return 3
    if "Response" in segments:
        return 0
    return 1 if not namespace else 2


def _prefix(namespace: str) -> str:
    segments = namespace.split(".")
    if "Response" in segments:
        return "Retrieved"
    if namespace.startswith("internal_"):
        core = re.sub(r"^internal_(document_|entities_)?", "", namespace)
        return pascal(re.sub(r"_v\d+$", "", core))
    last = segments[-1]
    if last in overrides.NAMESPACE_PREFIXES:
        return overrides.NAMESPACE_PREFIXES[last]
    return singular(pascal(last))


def _qualified(namespace: str) -> str:
    noise = {"iikoTransport", "PublicApi", "Contracts", "iikoNet", "Service", "Api", "Common", "Enums"}
    return "".join(pascal(s) for s in re.split(r"[.]", namespace) if s and s not in noise)


def assign_names(keys: set[str]) -> dict[str, str]:
    names: dict[str, str] = {}
    by_short: dict[str, list[str]] = defaultdict(list)
    for key in sorted(keys):
        if key in overrides.SCHEMA_NAMES:
            names[key] = overrides.SCHEMA_NAMES[key]
        elif key.endswith("WebHookEventInfo"):
            names[key] = _short(key).removesuffix("WebHookEventInfo") + "Event"
        else:
            by_short[_short(key)].append(key)
    for short, group in by_short.items():
        if len(group) == 1:
            names[group[0]] = short
            continue
        top = max(_priority(_namespace(k)) for k in group)
        tops = [k for k in group if _priority(_namespace(k)) == top]
        for key in group:
            bare = len(tops) == 1 and key == tops[0]
            names[key] = short if bare else _prefix(_namespace(key)) + short
    # Whatever still collides gets the fully qualified namespace.
    seen: dict[str, list[str]] = defaultdict(list)
    for key, name in names.items():
        seen[name].append(key)
    for group in seen.values():
        if len(group) > 1:
            for key in group:
                if key not in overrides.SCHEMA_NAMES:
                    names[key] = _qualified(_namespace(key)) + _short(key)
    final: dict[str, list[str]] = defaultdict(list)
    for key, name in names.items():
        final[name].append(key)
    clashes = {n: ks for n, ks in final.items() if len(ks) > 1}
    if clashes:
        msg = f"Ambiguous model names, add entries to codegen/overrides.py: {clashes}"
        raise ValueError(msg)
    return names


@dataclass
class _Ctx:
    module: str
    owner: str
    prop: str
    deps: set[str]
    as_input: bool = False
    in_request_model: bool = False


class Builder:
    def __init__(self, spec: Spec) -> None:
        self.spec = spec
        self.ops = spec.operations()
        self.hooks = spec.webhooks()
        self.models: dict[str, ModelDef] = {}
        self.enums: dict[str, EnumDef] = {}
        self.unions: dict[str, UnionDef] = {}
        self.inline: list[ModelDef] = []

        self.groups: dict[str, set[str]] = defaultdict(set)
        self.request_keys: set[str] = set()
        self.response_keys: set[str] = set()
        for op in self.ops:
            req = spec.closure([op.request] if op.request else [])
            resp = spec.closure([op.response] if op.response else [])
            self.request_keys |= req
            self.response_keys |= resp
            for key in req | resp:
                self.groups[key].add(op.group)
        for hook in self.hooks:
            keys = spec.closure([{"$ref": f"#/components/schemas/{hook.schema_key}"}])
            self.response_keys |= keys
            for key in keys:
                self.groups[key].add(WEBHOOKS_GROUP)
        self.keys = set(self.groups)
        self.wrappers = {k for k in self.keys if _short(k) == WRAPPER}
        named = self.keys - self.wrappers
        self.polymorphic = {k for k in named if self._discriminator(spec.schemas[k])}
        self.names = assign_names(named)
        self.class_names = {k: (f"{n}Base" if k in self.polymorphic else n) for k, n in self.names.items()}
        self.module = {k: self._module(k) for k in self.keys}
        self.literals: dict[str, tuple[str, Any, str]] = {}
        for key in self.polymorphic:
            disc = self._discriminator(spec.schemas[key])
            assert disc is not None
            for value, ref in disc["mapping"].items():
                self.literals.setdefault(spec.ref_key(ref), (disc["propertyName"], value, key))

    @staticmethod
    def _discriminator(schema: Schema) -> dict[str, Any] | None:
        disc = schema.get("discriminator")
        if isinstance(disc, dict) and disc.get("mapping"):
            return disc
        return None

    def _module(self, key: str) -> str:
        groups = self.groups[key]
        if len(groups) != 1:
            return COMMON
        (group,) = groups
        return overrides.GROUP_MODULES.get(group, re.sub(r"\W+", "_", group.split()[0].lower()))

    def is_enum(self, key: str) -> bool:
        return "enum" in self.spec.schemas[key]

    def ref_type(self, key: str, ctx: _Ctx) -> str:
        if key in self.wrappers:
            items = self.spec.schemas[key]["properties"]["items"]["items"]
            inner = self.render(items, ctx)
            ctx.deps.add(WRAPPER_CLASS)
            return f"{WRAPPER_CLASS}[{inner}]"
        name = self.names[key]
        ctx.deps.add(name)
        if ctx.as_input and not self.is_enum(key):
            return f"{name} | Mapping[str, Any]"
        return name

    def render(self, schema: Schema | None, ctx: _Ctx, *, top: bool = False) -> str:
        if not schema:
            return "Any"
        if "$ref" in schema:
            return self.ref_type(self.spec.ref_key(schema["$ref"]), ctx)
        if "allOf" in schema:
            if len(schema["allOf"]) == 1:
                return self.render(schema["allOf"][0], ctx)
            msg = f"{ctx.owner}.{ctx.prop}: a property with allOf of {len(schema['allOf'])} schemas is not supported"
            raise NotImplementedError(msg)
        if "oneOf" in schema:
            parts = dict.fromkeys(self.render(part, ctx) for part in schema["oneOf"])
            return " | ".join(parts)
        kind = schema.get("type")
        if isinstance(kind, str) and (match := _CONSTANT_STRING.match(kind)):
            ctx.deps.add("Literal")
            return f"Literal[{match.group(1)!r}]"
        if "enum" in schema and not top:
            ctx.deps.add("Literal")
            return f"Literal[{', '.join(repr(v) for v in schema['enum'])}]"
        if kind in ("array", "Array of strings <uuid>"):
            inner = self.render(schema.get("items"), ctx) if kind == "array" else "str"
            if ctx.as_input:
                ctx.deps.add("Sequence")
                return f"Sequence[{inner}]"
            return f"list[{inner}]"
        if kind == "object" or (kind is None and ("properties" in schema or "additionalProperties" in schema)):
            if schema.get("properties"):
                return self.inline_model(schema, ctx)
            extra = schema.get("additionalProperties")
            if isinstance(extra, dict) and extra:
                return f"dict[str, {self.render(extra, ctx)}]"
            return "dict[str, Any]"
        fmt = schema.get("format")
        if kind in ("string", "uuid"):
            if fmt == IIKO_DATETIME_FORMAT:
                return "datetime.datetime | str" if ctx.as_input else "IikoDateTime"
            if fmt == "date-time":
                return "datetime.datetime | str" if ctx.as_input else "IsoDateTime"
            if fmt == "date":
                return "datetime.date | str" if ctx.as_input else "datetime.date"
            return "str"
        if kind in ("integer", "int", "integer <int32>", "integer <int64>"):
            return "int"
        if kind in ("number", "float"):
            ctx.deps.add("Decimal")
            return "Decimal | float" if ctx.as_input else "Decimal"
        if kind in ("boolean", "bool"):
            return "bool"
        if kind == "enum":
            return "str"
        return "Any"

    def inline_model(self, schema: Schema, ctx: _Ctx) -> str:
        name = ctx.owner + pascal(ctx.prop)
        key = f"<inline {ctx.owner}.{ctx.prop}>"
        if not any(m.key == key for m in self.inline):
            inner = _Ctx(module=ctx.module, owner=name, prop="", deps=set())
            model = ModelDef(
                key=key,
                name=name,
                module=ctx.module,
                base=None,
                fields=[],
                description=clean_text(schema.get("description")),
                deps=inner.deps,
            )
            self.inline.append(model)
            model.fields = self.fields_of(schema, schema.get("properties", {}), set(), inner, set())
        ctx.deps.add(name)
        return f"{name} | Mapping[str, Any]" if ctx.as_input else name

    def make_field(self, alias: str, prop: Schema, *, required: bool, ctx: _Ctx) -> FieldDef:
        ctx.prop = alias
        annotation = self.render(prop, ctx)
        input_ctx = _Ctx(module=ctx.module, owner=ctx.owner, prop=alias, deps=ctx.deps, as_input=True)
        input_annotation = self.render(prop, input_ctx)
        nullable = bool(prop.get("nullable")) or any(p.get("nullable") for p in prop.get("allOf", []))
        # Required but nullable: the API wants the property present, so it defaults to None and is always sent.
        always_send = required and nullable
        required = required and not nullable
        if not required:
            annotation = f"{annotation} | None"
            input_annotation = f"{input_annotation} | None"
        description = clean_text(prop.get("description"))
        if prop.get("deprecated"):
            description = f"**Deprecated.** {description}".strip()
        if "default" in prop and prop["default"] is not None:
            description = f"{description}\n\nServer default: `{prop['default']}`.".strip()
        extras: dict[str, Any] = {}
        if ctx.in_request_model:
            for src, dst in (("minLength", "min_length"), ("maxLength", "max_length")):
                if src in prop and "str" in annotation:
                    extras[dst] = prop[src]
        return FieldDef(
            name=field_name(alias),
            alias=alias,
            annotation=annotation,
            input_annotation=input_annotation,
            required=required,
            description=description,
            extras=extras,
            default=None if required else "None",
            always_send=always_send,
        )

    def fields_of(
        self, schema: Schema, props: dict[str, Schema], required: set[str], ctx: _Ctx, inherited: set[str]
    ) -> list[FieldDef]:
        required = required | set(schema.get("required", []))
        result = []
        for alias, prop in props.items():
            fdef = self.make_field(alias, prop, required=alias in required, ctx=ctx)
            fdef.override = alias in inherited
            result.append(fdef)
        names = [f.name for f in result]
        if len(names) != len(set(names)):
            msg = f"Duplicate field names in {ctx.owner}: {names}"
            raise ValueError(msg)
        return result

    def inherited_aliases(self, key: str) -> set[str]:
        aliases: set[str] = set()
        schema = self.spec.schemas[key]
        for part in schema.get("allOf", []):
            if "$ref" in part:
                base_key = self.spec.ref_key(part["$ref"])
                base = self.spec.schemas[base_key]
                aliases |= set(base.get("properties", {}))
                for sub in base.get("allOf", []):
                    aliases |= set(sub.get("properties", {}))
                aliases |= self.inherited_aliases(base_key)
        return aliases

    def build_enum(self, key: str) -> EnumDef:
        schema = self.spec.schemas[key]
        values = schema["enum"]
        kind = "int" if schema.get("type") == "integer" else "str"
        labels = self.int_enum_labels(key, values) if kind == "int" else {}
        members = []
        used: set[str] = set()
        for value in values:
            label = labels.get(value) if kind == "int" else None
            name = upper_snake(label or str(value)) if (kind == "str" or label) else f"VALUE_{value}"
            if name in used:
                name = f"{name}_{len(used)}"
            used.add(name)
            members.append((name, value, label or ""))
        return EnumDef(
            key=key,
            name=self.names[key],
            module=self.module[key],
            kind=kind,
            members=members,
            description=clean_text(schema.get("description")),
        )

    def int_enum_labels(self, key: str, values: list[int]) -> dict[int, str]:
        """Integer enums have no member names in the spec; recover them from property descriptions."""
        ref = f"#/components/schemas/{key}"
        best: dict[int, str] = {}
        for schema in self.spec.schemas.values():
            for prop in schema.get("properties", {}).values():
                refs = [prop.get("$ref")] + [p.get("$ref") for p in prop.get("allOf", [])]
                if ref not in refs:
                    continue
                text = clean_text(prop.get("description"))
                found = {int(v): label.strip().rstrip(".") for v, label in _INT_ENUM_ITEM.findall(text)}
                found = {v: label for v, label in found.items() if v in values}
                if len(found) > len(best):
                    best = found
        return best if len(best) * 2 >= len(values) else {}

    def build_model(self, key: str) -> ModelDef:
        schema = self.spec.schemas[key]
        name = self.class_names[key]
        module = self.module[key]
        deps: set[str] = set()
        ctx = _Ctx(
            module=module,
            owner=name,
            prop="",
            deps=deps,
            in_request_model=key in self.request_keys and key not in self.response_keys,
        )
        base = None
        props: dict[str, Schema] = dict(schema.get("properties", {}))
        required = set(schema.get("required", []))
        for part in schema.get("allOf", []):
            if "$ref" in part:
                base_key = self.spec.ref_key(part["$ref"])
                if base is not None:
                    msg = f"{key}: multiple inheritance is not supported"
                    raise ValueError(msg)
                base = self.class_names[base_key]
                deps.add(base)
            else:
                props.update(part.get("properties", {}))
                required |= set(part.get("required", []))
        inherited = self.inherited_aliases(key)
        fields = self.fields_of(schema, props, required, ctx, inherited)
        discriminators: list[str] = [f.name for f in fields if f.always_send]
        if key in self.literals:
            alias, value, base_key = self.literals[key]
            fdef = next((f for f in fields if f.alias == alias), None)
            if fdef is None:
                fdef = self.make_field(alias, {}, required=False, ctx=ctx)
                fdef.override = True
                fields.insert(0, fdef)
            fdef.annotation, fdef.default = self.literal(base_key, alias, value, deps)
            fdef.input_annotation = fdef.annotation
            fdef.required = False
            fdef.override = fdef.override or alias in inherited
            discriminators.append(fdef.name)
        variants = None
        if key in self.polymorphic:
            disc = self._discriminator(schema)
            assert disc is not None
            discriminators += [f.name for f in fields if f.alias == disc["propertyName"]]
            variants = (field_name(disc["propertyName"]), tuple(str(v) for v in disc["mapping"]))
        return ModelDef(
            key=key,
            name=name,
            module=module,
            base=base,
            fields=fields,
            description=clean_text(schema.get("description")),
            discriminators=discriminators,
            deps=deps,
            request_only=ctx.in_request_model,
            variants=variants,
        )

    def literal(self, base_key: str, alias: str, value: Any, deps: set[str]) -> tuple[str, str]:
        """Annotation and default for a discriminator field narrowed to a single value."""
        deps.add("Literal")
        prop = self._find_property(base_key, alias)
        enum_key = None
        if prop:
            ref = prop.get("$ref") or next((p["$ref"] for p in prop.get("allOf", []) if "$ref" in p), None)
            enum_key = self.spec.ref_key(ref) if ref else None
        if enum_key and enum_key in self.keys and self.is_enum(enum_key):
            enum = self.names[enum_key]
            member = next((m for m in self.build_enum(enum_key).members if m[1] == value), None)
            if member:
                deps.add(enum)
                return f"Literal[{enum}.{member[0]}]", f"{enum}.{member[0]}"
        return f"Literal[{value!r}]", repr(value)

    def _find_property(self, key: str, alias: str) -> Schema | None:
        schema = self.spec.schemas[key]
        if alias in schema.get("properties", {}):
            return schema["properties"][alias]
        for part in schema.get("allOf", []):
            if "$ref" in part:
                found = self._find_property(self.spec.ref_key(part["$ref"]), alias)
                if found:
                    return found
            elif alias in part.get("properties", {}):
                return part["properties"][alias]
        return None

    def build_union(self, key: str) -> UnionDef:
        schema = self.spec.schemas[key]
        disc = self._discriminator(schema)
        assert disc is not None
        members = [(value, self.class_names[self.spec.ref_key(ref)]) for value, ref in disc["mapping"].items()]
        return UnionDef(
            key=key,
            name=self.names[key],
            module=self.module[key],
            discriminator_alias=disc["propertyName"],
            discriminator_name=field_name(disc["propertyName"]),
            members=members,
            fallback=self.class_names[key],
            description=clean_text(schema.get("description")),
            deps={name for _, name in members} | {self.class_names[key]},
        )

    def build_method(self, op: Operation) -> MethodDef:
        deps: set[str] = set()
        params: list[FieldDef] = []
        request_model = None
        body_param = None
        if op.request:
            key = self.spec.ref_key(op.request["$ref"]) if "$ref" in op.request else None
            if key and key in self.models and key not in self.polymorphic:
                request_model = self.names[key]
                deps.add(request_model)
                params = self.flat_fields(key)
                for p in params:
                    deps.update(self._names_in(p.input_annotation))
            else:
                owner = pascal("_".join(op.path))
                plain = _Ctx(module=COMMON, owner=owner, prop="body", deps=deps)
                as_input = _Ctx(module=COMMON, owner=owner, prop="body", deps=deps, as_input=True)
                body_param = FieldDef(
                    name="body",
                    alias="body",
                    annotation=self.render(op.request, plain),
                    input_annotation=self.render(op.request, as_input),
                    required=True,
                    description="Request body.",
                )
        if any(p.name in ("timeout", "self") for p in params):
            msg = f"{op.url}: request field clashes with a reserved parameter name"
            raise ValueError(msg)
        ctx = _Ctx(module="", owner="", prop="", deps=deps)
        if op.response is None:
            response = runtime = "None"
        else:
            response = self.render(op.response, ctx)
            runtime = response
            if response.startswith("list["):
                response = f"builtins.{response}"
        return MethodDef(
            op=op,
            name=op.path[-1],
            params=params,
            request_model=request_model,
            body_param=body_param,
            response=response,
            response_runtime=runtime,
            deps=deps,
        )

    def flat_fields(self, key: str) -> list[FieldDef]:
        """All fields of a model including inherited ones, required first (stable)."""
        chain = []
        model = self.models[key]
        by_name = {m.name: m for m in self.models.values()}
        while model:
            chain.append(model)
            model = by_name.get(model.base) if model.base else None
        fields: dict[str, FieldDef] = {}
        for model in reversed(chain):
            for f in model.fields:
                fields[f.name] = f
        ordered = list(fields.values())
        return [f for f in ordered if f.required] + [f for f in ordered if not f.required]

    def _names_in(self, annotation: str) -> set[str]:
        return set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", annotation))

    def build(self) -> IR:
        for key in sorted(self.keys - self.wrappers):
            if self.is_enum(key):
                self.enums[key] = self.build_enum(key)
        for key in sorted(self.keys - self.wrappers):
            if not self.is_enum(key):
                self.models[key] = self.build_model(key)
            if key in self.polymorphic:
                self.unions[key] = self.build_union(key)
        methods = [self.build_method(op) for op in self.ops]
        for model in self.inline:
            self.models[model.key] = model
        webhook_union = self.build_webhook_union()
        names = [e.name for e in self.enums.values()] + [m.name for m in self.models.values()]
        names += [u.name for u in self.unions.values()] + [WRAPPER_CLASS, webhook_union.name]
        clashes = sorted({name for name in names if names.count(name) > 1})
        if clashes:
            msg = f"Generated class names clash: {clashes}; add entries to codegen/overrides.py"
            raise ValueError(msg)
        module_of = {e.name: e.module for e in self.enums.values()}
        module_of |= {m.name: m.module for m in self.models.values()}
        module_of |= {u.name: u.module for u in self.unions.values()}
        module_of[WRAPPER_CLASS] = COMMON
        module_of[webhook_union.name] = webhook_union.module
        module_of[webhook_union.fallback] = webhook_union.module
        return IR(
            spec=self.spec,
            models=self.models,
            enums=self.enums,
            unions=self.unions,
            methods=methods,
            webhooks=self.hooks,
            webhook_union=webhook_union,
            module_of=module_of,
        )

    def build_webhook_union(self) -> UnionDef:
        module = self.module[self.hooks[0].schema_key] if self.hooks else COMMON
        fallback = ModelDef(
            key="<webhook fallback>",
            name="UnknownWebhookEvent",
            module=module,
            base=None,
            fields=[
                FieldDef("event_type", "eventType", "str", "str", required=True, description="Event type."),
                FieldDef(
                    "event_time",
                    "eventTime",
                    "IikoDateTime | None",
                    "IikoDateTime | None",
                    required=False,
                    description="Event time.",
                    default="None",
                ),
                FieldDef(
                    "organization_id",
                    "organizationId",
                    "str | None",
                    "str | None",
                    required=False,
                    description="Organization ID.",
                    default="None",
                ),
                FieldDef(
                    "correlation_id",
                    "correlationId",
                    "str | None",
                    "str | None",
                    required=False,
                    description="Correlation ID.",
                    default="None",
                ),
                FieldDef(
                    "event_info",
                    "eventInfo",
                    "Any",
                    "Any",
                    required=False,
                    description="Raw event details.",
                    default="None",
                ),
            ],
            description="Webhook event of a type unknown to this version of the library.",
            deps={"IikoDateTime"},
        )
        self.models[fallback.key] = fallback
        members = []
        for hook in self.hooks:
            value = _CONSTANT_STRING.match(self.spec.schemas[hook.schema_key]["properties"]["eventType"]["type"])
            assert value is not None
            members.append((value.group(1), self.class_names[hook.schema_key]))
        return UnionDef(
            key="<webhook union>",
            name="WebhookEvent",
            module=module,
            discriminator_alias="eventType",
            discriminator_name="event_type",
            members=members,
            fallback=fallback.name,
            description="Any webhook event sent by iikoCloud.",
            deps={name for _, name in members} | {fallback.name},
        )


def build(spec: Spec) -> IR:
    return Builder(spec).build()


__all__ = ["IR", "EnumDef", "FieldDef", "MethodDef", "ModelDef", "UnionDef", "build", "clean_text", "safe_attr"]
