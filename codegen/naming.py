"""Identifier helpers: snake_case/PascalCase conversion and Python-safe names."""

from __future__ import annotations

import keyword
import re

from pydantic.alias_generators import to_camel

# Attributes of ``pydantic.BaseModel`` that a field must not shadow.
_BASEMODEL_ATTRS = frozenset(
    {
        "construct",
        "copy",
        "dict",
        "fields",
        "from_orm",
        "json",
        "parse_file",
        "parse_obj",
        "parse_raw",
        "schema",
        "schema_json",
        "update_forward_refs",
        "validate",
    }
)

# Names used in generated annotations; a field with such a name would shadow them in the class body.
_TYPE_NAMES = frozenset(
    {"bool", "builtins", "bytes", "datetime", "dict", "float", "int", "list", "set", "str", "tuple"}
)

_ACRONYM_BOUNDARY = re.compile(r"([A-Z]+)([A-Z][a-z])")
_WORD_BOUNDARY = re.compile(r"([a-z\d])([A-Z])")
_NON_IDENT = re.compile(r"[^0-9a-zA-Z_]+")


def snake(name: str) -> str:
    """Convert ``camelCase``/``PascalCase``/``kebab-case`` to ``snake_case``."""
    name = _ACRONYM_BOUNDARY.sub(r"\1_\2", name)
    name = _WORD_BOUNDARY.sub(r"\1_\2", name)
    name = _NON_IDENT.sub("_", name)
    return re.sub(r"_+", "_", name).strip("_").lower()


def pascal(name: str) -> str:
    """Convert any identifier-ish string to ``PascalCase``, keeping inner capitals."""
    parts = re.split(r"[^0-9a-zA-Z]+", name)
    return "".join(p[:1].upper() + p[1:] for p in parts if p)


def upper_snake(value: str) -> str:
    """Build an enum member name from an arbitrary value or description."""
    name = snake(value).upper()
    if not name:
        name = "EMPTY"
    if name[0].isdigit():
        name = f"V_{name}"
    return name


def safe_attr(name: str) -> str:
    """Make ``name`` usable as a Python attribute or keyword argument."""
    if not name:
        return "value_"
    if name[0].isdigit():
        name = f"n_{name}"
    if keyword.iskeyword(name):  # soft keywords (match, case, type) are valid names
        return f"{name}_"
    return name


def field_name(alias: str) -> str:
    """Python name of a model field for the JSON property ``alias``."""
    name = safe_attr(snake(alias))
    if name in _BASEMODEL_ATTRS or name in _TYPE_NAMES or name.startswith("model_"):
        name = f"{name}_"
    return name


def needs_explicit_alias(name: str, alias: str) -> bool:
    """Whether the default ``to_camel`` alias generator would produce a wrong alias."""
    return to_camel(name) != alias


def plural(word: str) -> str:
    if word.endswith("y") and word[-2:-1] not in "aeiou":
        return word[:-1] + "ies"
    if word.endswith(("s", "x", "ch", "sh")):
        return word + "es"
    return word + "s"


def singular(word: str) -> str:
    if word.endswith("ies"):
        return word[:-3] + "y"
    if word.endswith("sses"):
        return word[:-2]
    if word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word
