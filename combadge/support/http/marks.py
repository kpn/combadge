"""Generic marks applicable to a variety of protocols."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, TypeVar, Union

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


class PathMark(MethodMark):
    """
    Specifies a URL path.

    Example:
        >>> @path("/hello/world")
        >>> def call() -> None: ...

        >>> @path("/hello/{name}")
        >>> def call(name: str) -> None: ...

        >>> @path(lambda name, **_: f"/hello/{name}")
        >>> def call(name: str) -> None: ...

    Notes:
        - Always refer to parameters with their names. Positional arguments, e.g. `{0}` are
          intentionally unsupported.
    """

    _factory: Callable[..., str]
    __slots__ = ("_factory",)

    def __init__(self, path_or_factory: Union[str, Callable[..., str]]) -> None:  # noqa: D107
        if callable(path_or_factory):
            self._factory = path_or_factory
        else:
            self._factory = path_or_factory.format

    def prepare_request(self, request: Dict[str, Any], _arguments: Dict[str, Any]) -> None:  # noqa: D102
        request[RequiresPath.KEY] = self._factory(**_arguments)


path = make_method_mark_decorator(PathMark)
