"""Base classes and types shared by all generated models."""

from __future__ import annotations

import datetime
import math
from collections.abc import Iterable
from decimal import Decimal
from enum import Enum, IntEnum, StrEnum
from typing import Annotated, Any, ClassVar, Generic, Self, TypeVar

from pydantic import BaseModel, ConfigDict, Discriminator, PlainSerializer, PrivateAttr, ValidationInfo, model_validator
from pydantic.alias_generators import to_camel

LENIENT = "iikocloudapi.lenient"
"""Validation context flag used when parsing API responses: unknown fields and enum values are tolerated."""
LENIENT_CONTEXT = {LENIENT: True}

UNKNOWN = "__unknown__"
"""Discriminator tag for union members that are unknown to this version of the library."""


class OpenStrEnum(StrEnum):
    """String enum that tolerates values added to the API after this library was released.

    Unknown values become pseudo-members: they compare equal to the raw string and have ``is_known == False``.
    """

    @classmethod
    def _missing_(cls, value: object) -> Self | None:
        if isinstance(value, str):
            member = str.__new__(cls, value)
            member._name_ = value
            member._value_ = value
            return member
        return None

    @property
    def is_known(self) -> bool:
        """``False`` for values that are not declared in the specification this library was generated from."""
        return type(self)._value2member_map_.get(self._value_) is self


class OpenIntEnum(IntEnum):
    """Integer counterpart of :class:`OpenStrEnum`."""

    @classmethod
    def _missing_(cls, value: object) -> Self | None:
        if isinstance(value, int) and not isinstance(value, bool):
            member = int.__new__(cls, value)
            member._name_ = f"UNKNOWN_{value}"
            member._value_ = value
            return member
        return None

    @property
    def is_known(self) -> bool:
        """``False`` for values that are not declared in the specification this library was generated from."""
        return type(self)._value2member_map_.get(self._value_) is self


def format_iiko_datetime(value: datetime.datetime) -> str:
    """Format a datetime the way iikoCloud expects it: ``yyyy-MM-dd HH:mm:ss.fff``."""
    return value.strftime("%Y-%m-%d %H:%M:%S.") + f"{value.microsecond // 1000:03d}"


IikoDateTime = Annotated[datetime.datetime, PlainSerializer(format_iiko_datetime, return_type=str, when_used="always")]
"""A ``datetime`` that is (de)serialised in iikoCloud's ``yyyy-MM-dd HH:mm:ss.fff`` format.

iikoCloud uses the local time of the organization; naive datetimes are sent as is.
"""

IsoDateTime = Annotated[
    datetime.datetime, PlainSerializer(datetime.datetime.isoformat, return_type=str, when_used="always")
]
"""A ``datetime`` that is serialised in ISO 8601 format (used by a few newer endpoints)."""


def _unknown_enum(value: Any) -> Enum | None:
    if isinstance(value, OpenStrEnum | OpenIntEnum):
        return None if value.is_known else value
    if isinstance(value, list | tuple):
        return next((found for item in value if (found := _unknown_enum(item)) is not None), None)
    if isinstance(value, dict):
        return _unknown_enum(list(value.values()))
    return None


_ALWAYS_SENT: dict[type, frozenset[str]] = {}


def _always_sent(cls: type) -> frozenset[str]:
    found = _ALWAYS_SENT.get(cls)
    if found is None:
        found = _ALWAYS_SENT[cls] = frozenset(
            name for klass in cls.__mro__ for name in klass.__dict__.get("__always_sent__", ())
        )
    return found


class IikoModel(BaseModel):
    """Base class of every model in :mod:`iikocloudapi.models`.

    Models are strict when you build them (unknown fields and enum values raise ``ValidationError``) and lenient
    when they are parsed from an API response (unknown fields are kept in ``model_extra``, unknown enum values become
    pseudo-members), so new fields on the iikoCloud side never break your code.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        validate_by_name=True,
        validate_by_alias=True,
        serialize_by_alias=True,
        extra="allow",
        defer_build=True,
        protected_namespaces=(),
    )

    # Sent even when not set: discriminators and fields the API requires to be present, possibly as null.
    __always_sent__: ClassVar[tuple[str, ...]] = ()
    # Set on the base model of a tagged union: (discriminator field, known tags).
    __variants__: ClassVar[tuple[str, tuple[str, ...]] | None] = None

    # Parsed from an API response: may carry fields and values unknown to this library, and may be sent back as is.
    _from_response: bool = PrivateAttr(default=False)

    def model_post_init(self, context: Any, /) -> None:  # noqa: ARG002
        always = _always_sent(type(self))
        if always:
            self.__pydantic_fields_set__.update(always)

    @model_validator(mode="after")
    def _reject_unknown(self, info: ValidationInfo) -> Self:
        if info.context and info.context.get(LENIENT):
            self._from_response = True
            return self
        if self._from_response:
            return self
        if self.__pydantic_extra__:
            msg = f"unknown field(s): {', '.join(sorted(self.__pydantic_extra__))}"
            raise ValueError(msg)
        if self.__variants__ is not None:
            name, tags = self.__variants__
            tag = getattr(self, name, None)
            tag = tag.value if isinstance(tag, Enum) else tag
            if str(tag) not in tags:
                msg = f"{name}: {tag!r} is not one of {', '.join(map(repr, tags))}"
                raise ValueError(msg)
        for name, value in self.__dict__.items():
            unknown = _unknown_enum(value)
            if unknown is not None:
                allowed = ", ".join(repr(m.value) for m in type(unknown))
                msg = f"{name}: {unknown.value!r} is not a valid {type(unknown).__name__} (expected one of {allowed})"
                raise ValueError(msg)
        return self


T = TypeVar("T")


class OrganizationItems(IikoModel, Generic[T]):
    """Items that belong to a single organization."""

    organization_id: str
    """Organization ID."""
    items: list[T]
    """Items of the organization."""


def discriminator(alias: str, name: str, known: Iterable[Any]) -> Discriminator:
    """Discriminator for a tagged union that falls back to the base model for unknown tags."""
    tags = frozenset(str(value) for value in known)

    def tag(value: Any) -> str:
        found = value.get(alias, value.get(name)) if isinstance(value, dict) else getattr(value, name, None)
        if isinstance(found, Enum):
            found = found.value
        found = str(found)
        return found if found in tags else UNKNOWN

    return Discriminator(tag)


def number_to_json(value: Decimal) -> int | float:
    """JSON representation of a ``Decimal``: integral values become ``int``, others the closest ``float``.

    The iikoCloud API declares all numbers as ``double``, so the shortest float representation is exact.
    """
    if not value.is_finite():
        msg = f"{value} cannot be sent to iikoCloud: JSON has no NaN or infinity"
        raise ValueError(msg)
    if value == value.to_integral_value() and abs(value) < 2**53:
        return int(value)
    result = float(value)
    if math.isinf(result):
        msg = f"{value} is out of the range of numbers iikoCloud accepts"
        raise ValueError(msg)
    return result


def to_jsonable(value: Any) -> Any:  # noqa: PLR0911
    """Convert a request body (models, decimals, datetimes, enums) to plain JSON types."""
    if isinstance(value, BaseModel):
        value = value.model_dump(mode="python", by_alias=True, exclude_unset=True)
    if isinstance(value, dict):
        return {str(k): to_jsonable(v) for k, v in value.items()}
    if isinstance(value, list | tuple | set | frozenset):
        return [to_jsonable(v) for v in value]
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Decimal):
        return number_to_json(value)
    if isinstance(value, datetime.datetime):
        return format_iiko_datetime(value)
    if isinstance(value, datetime.date):
        return value.isoformat()
    return value


__all__ = [
    "LENIENT",
    "LENIENT_CONTEXT",
    "UNKNOWN",
    "IikoDateTime",
    "IikoModel",
    "IsoDateTime",
    "OpenIntEnum",
    "OpenStrEnum",
    "OrganizationItems",
    "discriminator",
    "format_iiko_datetime",
    "number_to_json",
    "to_jsonable",
]
