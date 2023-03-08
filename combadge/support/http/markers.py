"""Markers for HTTP-compatible protocols."""

from dataclasses import dataclass
from typing import Any, Callable, Dict, Generic, Tuple, Union

from typing_extensions import TypeAlias

from combadge.core.markers.method import MethodMarker
from combadge.core.markers.parameter import ParameterMarker
from combadge.core.typevars import FunctionT
from combadge.support.http.abc import RequiresMethod, RequiresPath, SupportsHeaders, SupportsQueryParams


@dataclass
class HeaderParameterMarker(ParameterMarker[SupportsHeaders]):
    """Marker class for the [`Header`][combadge.support.http.markers.Header] alias."""

    name: str
    __slots__ = ("name",)

    def prepare_request(self, request: SupportsHeaders, value: Any) -> None:  # noqa: D102
        request.headers.append((self.name, value))


Header: TypeAlias = HeaderParameterMarker
"""Mark a parameter as a header value."""


class _PathMarker(Generic[FunctionT], MethodMarker[RequiresPath, FunctionT, FunctionT]):
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


def path(path_or_factory: Union[str, Callable[..., str]]) -> Callable[[FunctionT], FunctionT]:
    """
    Specify a URL path.

    Examples:
        >>> @path("/hello/world")
        >>> def call() -> None: ...

        >>> @path("/hello/{name}")
        >>> def call(name: str) -> None: ...

        >>> @path(lambda name, **_: f"/hello/{name}")
        >>> def call(name: str) -> None: ...
    """
    return _PathMarker[Any](path_or_factory).mark


@dataclass
class _HttpMethodMarker(Generic[FunctionT], MethodMarker[RequiresMethod, FunctionT, FunctionT]):
    method: str

    def prepare_request(  # noqa: D102
        self,
        request: RequiresMethod,
        _args: Tuple[Any, ...],
        _kwargs: Dict[str, Any],
    ) -> None:
        request.method = self.method


def http_method(method: str) -> Callable[[FunctionT], FunctionT]:
    """Specify an HTTP method."""
    return _HttpMethodMarker[Any](method).mark


@dataclass
class QueryParameterMarker(ParameterMarker[SupportsQueryParams]):
    """Marker class for the [`QueryParam`][combadge.support.http.markers.QueryParam] alias."""

    name: str
    __slots__ = ("name",)

    def prepare_request(self, request: SupportsQueryParams, value: Any) -> None:  # noqa: D102
        request.query_params.append((self.name, value))


QueryParam: TypeAlias = QueryParameterMarker
"""
Mark a parameter as a query parameter.

Notes:

    - Multiple arguments with the same query parameter name are allowed
"""
