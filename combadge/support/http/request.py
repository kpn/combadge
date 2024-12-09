from __future__ import annotations

from collections.abc import Hashable
from dataclasses import dataclass
from enum import Enum
from inspect import BoundArguments
from typing import Any, Callable, Generic

from annotated_types import SLOTS
from typing_extensions import override

from combadge._helpers.pydantic import get_type_adapter
from combadge.core.markers.method import MethodMarker
from combadge.core.markers.parameter import ParameterMarker
from combadge.core.typevars import FunctionT
from combadge.support.common.request import BaseBackendRequest
from combadge.support.http.abc import (
    HttpRequestFormData,
    HttpRequestHeaders,
    HttpRequestMethod,
    HttpRequestPayload,
    HttpRequestQueryParams,
    HttpRequestUrlPath,
)


@dataclass(**SLOTS)
class CustomHeader(ParameterMarker[HttpRequestHeaders]):
    """
    Mark a parameter as a header value. Argument is passed «as is» during a service call.

    Examples:
        >>> class Service(Protocol):
        >>>     def service(self, accept_language: Annotated[str, CustomHeader("Accept-Language")]):
        >>>         ...
    """

    name: str

    @override
    def __call__(self, request: HttpRequestHeaders, value: Any) -> None:  # noqa: D102
        request.http_headers.append((self.name, value))


@dataclass(init=False, **SLOTS)
class Path(MethodMarker[HttpRequestUrlPath, FunctionT], Generic[FunctionT]):  # noqa: D101
    _factory: Callable[[BoundArguments], str]

    def __init__(self, path_or_factory: str | Callable[[BoundArguments], str]) -> None:  # noqa: D107
        if callable(path_or_factory):
            self._factory = path_or_factory
        else:

            def factory(arguments: BoundArguments) -> str:
                # The `arguments.arguments` will contain the positional arguments too.
                # This is intentional to allow referring to positional arguments by their indexes and names.
                return path_or_factory.format(*arguments.args, **arguments.arguments)

            self._factory = factory

    @override
    def prepare_request(self, request: HttpRequestUrlPath, arguments: BoundArguments) -> None:  # noqa: D102
        request.url_path = self._factory(arguments)


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
class HttpMethod(MethodMarker[HttpRequestMethod, FunctionT], Generic[FunctionT]):  # noqa: D101
    method: str

    @override
    def prepare_request(self, request: HttpRequestMethod, _arguments: BoundArguments) -> None:  # noqa: D102
        request.method = self.method


def http_method(method: str) -> Callable[[FunctionT], FunctionT]:
    """
    Specify an HTTP method.

    Examples:
        >>> @http_method("POST")
        >>> def call() -> None: ...
    """
    return HttpMethod[Any](method).mark


@dataclass(**SLOTS)
class QueryParam(ParameterMarker[HttpRequestQueryParams]):
    """
    Mark parameter as a query parameter.

    Examples:
        >>> def call(query: Annotated[str, QueryParam("query")]) -> ...:
        >>>     ...
    """

    name: str

    @override
    def __call__(self, request: HttpRequestQueryParams, value: Any) -> None:  # noqa: D102
        request.query_params.append((self.name, value.value if isinstance(value, Enum) else value))


@dataclass(**SLOTS)
class QueryArrayParam(ParameterMarker[HttpRequestQueryParams]):
    """
    Mark parameter as an array-like query parameter.

    Supports any iterable value as a call argument.

    Examples:
        >>> def call(query: Annotated[list[str], QueryParam("query")]) -> ...:
        >>>     ...

        >>> def call(query: Annotated[Iterable[str], QueryParam("query")]) -> ...:
        >>>     ...
    """

    name: str

    @override
    def __call__(self, request: HttpRequestQueryParams, value: Any) -> None:  # noqa: D102
        for sub_value in value:
            request.query_params.append((self.name, sub_value.value if isinstance(sub_value, Enum) else sub_value))


@dataclass(**SLOTS)
class Payload(ParameterMarker[HttpRequestPayload]):
    """
    Mark parameter as a request payload.

    An argument gets converted to a dictionary and passed over to a backend.

    Examples:
        >>> def call(body: Annotated[BodyModel, Payload()]) -> ...:
        >>>     ...
    """

    exclude_unset: bool = False
    by_alias: bool = False

    @override
    def __call__(self, request: HttpRequestPayload, value: Any) -> None:  # noqa: D102
        value_type = type(value)
        assert isinstance(value_type, Hashable)
        value = get_type_adapter(value_type).dump_python(
            value,
            by_alias=self.by_alias,
            exclude_unset=self.exclude_unset,
        )
        if request.payload is None:
            request.payload = value
        elif isinstance(request.payload, dict):
            request.payload.update(value)  # merge into the existing payload
        else:
            raise ValueError(f"attempting to merge `{value_type}` into `{type(request.payload)}`")

    def __class_getitem__(cls, item: type[Any]) -> Any:
        raise NotImplementedError("the shortcut is no longer supported, use `Annotated[..., Payload()]`")


@dataclass(**SLOTS)
class Field(ParameterMarker[HttpRequestPayload]):
    """
    Mark a parameter as a value of a separate payload field.

    Examples:
        >>> def call(param: Annotated[int, Field("param")]) -> ...:
        >>>     ...

    Notes:
        - Enum values are passed by value
    """

    name: str

    @override
    def __call__(self, request: HttpRequestPayload, value: Any) -> None:  # noqa: D102
        if request.payload is None:
            request.payload = {}
        request.payload[self.name] = value.value if isinstance(value, Enum) else value


@dataclass(**SLOTS)
class FormData(ParameterMarker[HttpRequestFormData]):
    """
    Mark parameter as a request form data.

    An argument gets converted to a dictionary and passed over to a backend.

    Examples:
        >>> def call(body: Annotated[FormModel, FormData()]) -> ...:
        >>>     ...
    """

    @override
    def __call__(self, request: HttpRequestFormData, value: Any) -> None:  # noqa: D102
        value_type = type(value)
        assert isinstance(value_type, Hashable)
        value = get_type_adapter(value_type).dump_python(value, by_alias=True)
        if not isinstance(value, dict):
            raise TypeError(f"form data requires a dictionary, got {type(value)}")
        for item_name, item_value in value.items():
            request.append_form_field(item_name, item_value)

    def __class_getitem__(cls, item: type[Any]) -> Any:
        raise NotImplementedError("the shortcut is no longer supported, use `Annotated[..., FormData()]`")


@dataclass(**SLOTS)
class FormField(ParameterMarker[HttpRequestFormData]):
    """
    Mark a parameter as a separate form field value.

    Examples:
        >>> def call(param: Annotated[int, FormField("param")]) -> ...:
        >>>     ...

    Notes:
        - Multiple arguments with the same field name are allowed
        - [`FormData`][combadge.support.http.request.FormData] marker's fields get merged with `FormField` ones (if present)
        - Enum values are passed by value
    """  # noqa: E501

    name: str

    @override
    def __call__(self, request: HttpRequestFormData, value: Any) -> None:  # noqa: D102
        request.append_form_field(self.name, value.value if isinstance(value, Enum) else value)


@dataclass(**SLOTS)
class Request(
    BaseBackendRequest,
    HttpRequestFormData,
    HttpRequestHeaders,
    HttpRequestMethod,
    HttpRequestPayload,
    HttpRequestQueryParams,
    HttpRequestUrlPath,
):
    """Backend-agnostic HTTP request."""
