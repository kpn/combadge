"""Marks for HTTP-compatible requests."""

from dataclasses import dataclass
from typing import Any, TypeVar, Union

from typing_extensions import Annotated, TypeAlias

from combadge.core.mark import ParameterMark
from combadge.support.http.abc import RequiresBody, SupportsBody, SupportsHeaders

T = TypeVar("T")


@dataclass
class BodyParameterMark(ParameterMark[Union[RequiresBody, SupportsBody]]):
    """Designates a parameter a service call's request body."""

    __slots__ = ()

    def prepare_request(self, request: Union[RequiresBody, SupportsBody], value: Any) -> None:  # noqa: D102
        request.body = value


Body: TypeAlias = Annotated[T, BodyParameterMark()]


@dataclass
class HeaderParameterMark(ParameterMark[SupportsHeaders]):
    """Designates parameter as a service call's additional header."""

    name: str
    __slots__ = ("name",)

    def prepare_request(self, request: SupportsHeaders, value: Any) -> None:  # noqa: D102
        request.headers.append((self.name, value))


Header: TypeAlias = HeaderParameterMark
