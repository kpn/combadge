"""Marks for HTTP-compatible requests."""
import http
from dataclasses import dataclass
from typing import Any, Callable, Dict, Tuple, TypeVar, Union

from typing_extensions import Annotated, TypeAlias

from combadge.core.mark import MethodMark, ParameterMark
from combadge.core.mark.response import ResponseMark
from combadge.core.typevars import Identity
from combadge.support.http.abc import (
    RequiresBody,
    RequiresMethod,
    RequiresPath,
    SupportsBody,
    SupportsHeaders,
    SupportsQueryParams,
)

_T = TypeVar("_T")


@dataclass
class BodyParameterMark(ParameterMark[Union[RequiresBody, SupportsBody]]):
    """Designates a parameter a service call's request body."""

    __slots__ = ()

    def prepare_request(self, request: Union[RequiresBody, SupportsBody], value: Any) -> None:  # noqa: D102
        request.body = value


Body: TypeAlias = Annotated[_T, BodyParameterMark()]


@dataclass
class HeaderParameterMark(ParameterMark[SupportsHeaders]):
    """Designates parameter as a service call's additional header."""

    name: str
    __slots__ = ("name",)

    def prepare_request(self, request: SupportsHeaders, value: Any) -> None:  # noqa: D102
        request.headers.append((self.name, value))


Header: TypeAlias = HeaderParameterMark


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
class _HttpMethodMark(MethodMark[RequiresMethod]):
    method: str  # TODO: enum?

    def prepare_request(  # noqa: D102
        self,
        request: RequiresMethod,
        _args: Tuple[Any, ...],
        _kwargs: Dict[str, Any],
    ) -> None:
        request.method = self.method


def http_method(method: str) -> Identity:
    """Specify an HTTP method."""
    return _HttpMethodMark(method).mark


@dataclass
class QueryParameterMark(ParameterMark[SupportsQueryParams]):
    """Designates parameter as a service call's query parameter."""

    name: str
    __slots__ = ("name",)

    def prepare_request(self, request: SupportsQueryParams, value: Any) -> None:  # noqa: D102
        request.query_params.append((self.name, value))


QueryParam: TypeAlias = QueryParameterMark

status_code_response_mark = ResponseMark("status_code_response_mark")
"""Mark an attribute as a response status code."""

StatusCode: TypeAlias = Annotated[http.HTTPStatus, status_code_response_mark]
"""Mark an attribute as a response status code."""
