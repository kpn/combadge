from __future__ import annotations

from dataclasses import dataclass
from inspect import BoundArguments
from typing import Any, Callable, Generic, TypedDict

from annotated_types import SLOTS
from typing_extensions import override

from combadge.core.markers import Marker
from combadge.core.typevars import FunctionT


class HttpRequestSpecification(TypedDict):
    method: str
    path: str


@dataclass(init=False, **SLOTS)
class Path(Marker[HttpRequestSpecification, FunctionT], Generic[FunctionT]):  # noqa: D101
    _factory: Callable[[BoundArguments], str]

    def __init__(self, path_or_factory: str | Callable[[BoundArguments], str]) -> None:  # noqa: D107
        if callable(path_or_factory):
            self._factory = path_or_factory
        else:
            self._factory = lambda arguments: path_or_factory.format(*arguments.args, **arguments.arguments)

    @override
    def prepare_request(self, request: HttpRequestSpecification, arguments: BoundArguments) -> None:  # noqa: D102
        request["path"] = self._factory(arguments)


def path(path_or_factory: str | Callable[..., str]) -> Callable[[FunctionT], FunctionT]:
    """
    Specify a URL path.

    Examples:
        >>> @path("/hello/world")
        >>> def call() -> None: ...

        >>> @path("/hello/{name}")
        >>> def call(name: str) -> None: ...

        >>> @path("/hello/{0}")
        >>> def call(name: str) -> None: ...

        >>> @path(lambda name, **_: f"/hello/{name}")
        >>> def call(name: str) -> None: ...
    """
    return Path[Any](path_or_factory).mark


@dataclass(**SLOTS)
class HttpMethod(Marker[HttpRequestSpecification, FunctionT], Generic[FunctionT]):  # noqa: D101
    method: str

    @override
    def prepare_request(self, request: HttpRequestSpecification, _arguments: BoundArguments) -> None:  # noqa: D102
        request["method"] = self.method


def http_method(method: str) -> Callable[[FunctionT], FunctionT]:
    """
    Specify an HTTP method.

    Examples:
        >>> @http_method("POST")
        >>> def call() -> None: ...
    """
    return HttpMethod[Any](method).mark
