"""Generic marks applicable to a variety of protocols."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Tuple, TypeVar, Union

from typing_extensions import TypeAlias

from combadge.core.mark import MethodMark, ParameterMark
from combadge.core.typevars import Identity
from combadge.support.rest.abc import RequiresMethod, RequiresPath, SupportsQueryParams

T = TypeVar("T")


class _PathMark(MethodMark[RequiresPath]):
    _factory: Callable[..., str]
    __slots__ = ("_factory",)

    def __init__(self, path_or_factory: Union[str, Callable[..., str]]) -> None:  # noqa: D107
        if callable(path_or_factory):
            self._factory = path_or_factory
        else:
            self._factory = path_or_factory.format

    def prepare_request(  # noqa: D102
        self,
        request: RequiresPath,
        args: Tuple[Any, ...],
        kwargs: Dict[str, Any],
    ) -> None:
        request.path = self._factory(*args, **kwargs)


def path(path_or_factory: Union[str, Callable[..., str]]) -> Identity:
    """
    Specify a URL path.

    Example:
        >>> @path("/hello/world")
        >>> def call() -> None: ...

        >>> @path("/hello/{name}")
        >>> def call(name: str) -> None: ...

        >>> @path(lambda name, **_: f"/hello/{name}")
        >>> def call(name: str) -> None: ...
    """
    return _PathMark(path_or_factory).mark


@dataclass
class _RestMethodMark(MethodMark[RequiresMethod]):
    method: str  # TODO: enum?

    def prepare_request(  # noqa: D102
        self,
        request: RequiresMethod,
        _args: Tuple[Any, ...],
        _kwargs: Dict[str, Any],
    ) -> None:
        request.method = self.method


def method(method: str) -> Identity:
    """Specify a HTTP/REST method."""
    return _RestMethodMark(method).mark


@dataclass
class QueryParameterMark(ParameterMark[SupportsQueryParams]):
    """Designates parameter as a service call's query parameter."""

    name: str
    __slots__ = ("name",)

    def prepare_request(self, request: SupportsQueryParams, value: Any) -> None:  # noqa: D102
        request.query_params.append((self.name, value))


QueryParam: TypeAlias = QueryParameterMark
