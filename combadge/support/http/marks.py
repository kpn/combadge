from dataclasses import dataclass
from typing import Any, TypeVar, cast

from pydantic import BaseModel
from typing_extensions import Annotated, TypeAlias

from combadge.core.mark import ParameterMark
from combadge.support.http.abc import RequiresBody, SupportsHeaders

T = TypeVar("T")


@dataclass
class BodyParameterMark(ParameterMark):
    """Designates a parameter a service call's request body."""

    __slots__ = ()

    def prepare_request(self, request: BaseModel, value: Any) -> None:  # noqa: D102
        cast(RequiresBody, request).body = value


Body: TypeAlias = Annotated[T, BodyParameterMark()]


@dataclass
class HeaderParameterMark(ParameterMark):
    """Designates parameter as a service call's additional header."""

    name: str
    __slots__ = ("name",)

    def prepare_request(self, request: BaseModel, value: Any) -> None:  # noqa: D102
        cast(SupportsHeaders, request).headers.append((self.name, value))


Header: TypeAlias = HeaderParameterMark
