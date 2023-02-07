"""Generic marks applicable to a variety of protocols."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, TypeVar

from typing_extensions import Annotated, TypeAlias

from combadge.core.mark import MethodMark, ParameterMark, make_method_mark_decorator
from combadge.support.http.abc import RequiresBody, RequiresPath, SupportsHeaders

T = TypeVar("T")


@dataclass
class BodyParameterMark(ParameterMark):
    """Designates a parameter a service call's request body."""

    __slots__ = ()

    def prepare_request(self, request: Dict[str, Any], value: Any) -> None:  # noqa: D102
        request[RequiresBody.KEY] = value


Body: TypeAlias = Annotated[T, BodyParameterMark()]


@dataclass
class HeaderParameterMark(ParameterMark):
    """Designates parameter as a service call's additional header."""

    name: str
    __slots__ = ("name",)

    def prepare_request(self, request: Dict[str, Any], value: Any) -> None:  # noqa: D102
        request.setdefault(SupportsHeaders.KEY, []).append((self.name, value))


Header: TypeAlias = HeaderParameterMark


@dataclass
class PathFormatMark(MethodMark):
    """
    Specifies a URL path format.

    Example:
        >>> @path_format("/hello/{name}")

    Notes:
        - Referencing parameters by their position, e.g. `{0}` is not possible. Refer to them by their names.
    """

    format_: str
    __slots__ = ("format_",)

    def prepare_request(self, request: Dict[str, Any], arguments: Dict[str, Any]) -> None:  # noqa: D102
        request[RequiresPath.KEY] = self.format_.format(**arguments)


path_format = make_method_mark_decorator(PathFormatMark)


@dataclass
class PathFactoryMark(MethodMark):
    """
    Specifies a URL path factory.

    Example:
        >>> @path_factory(lambda name, **_: f"/hello/{name}")
    """

    factory: Callable[..., str]
    __slots__ = ("factory",)

    def prepare_request(self, request: Dict[str, Any], arguments: Dict[str, Any]) -> None:  # noqa: D102
        request[RequiresPath.KEY] = self.factory(**arguments)


path_factory = make_method_mark_decorator(PathFactoryMark)
