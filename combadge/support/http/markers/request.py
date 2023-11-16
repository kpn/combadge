from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from inspect import BoundArguments
from typing import TYPE_CHECKING, Any, Callable, Generic, TypeVar

from typing_extensions import Annotated, TypeAlias, override

from combadge._helpers.dataclasses import SLOTS
from combadge._helpers.pydantic import get_type_adapter
from combadge.core.markers.method import MethodMarker
from combadge.core.markers.parameter import ParameterMarker
from combadge.core.typevars import FunctionT
from combadge.support.http.abc import (
    ContainsFormData,
    ContainsHeaders,
    ContainsMethod,
    ContainsPayload,
    ContainsQueryParams,
    ContainsUrlPath,
)

_T = TypeVar("_T")


@dataclass(**SLOTS)
class CustomHeader(ParameterMarker[ContainsHeaders]):
    """
    Mark a parameter as a header value. Argument is passed «as is» during a service call.

    Examples:
        >>> class Service(Protocol):
        >>>     def service(self, accept_language: Annotated[str, CustomHeader("Accept-Language")]):
        >>>         ...
    """

    name: str

    @override
    def __call__(self, request: ContainsHeaders, value: Any) -> None:  # noqa: D102
        request.headers.append((self.name, value))


@dataclass(init=False, **SLOTS)
class Path(Generic[FunctionT], MethodMarker[ContainsUrlPath, FunctionT]):  # noqa: D101
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
    def prepare_request(self, request: ContainsUrlPath, arguments: BoundArguments) -> None:  # noqa: D102
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
class HttpMethod(Generic[FunctionT], MethodMarker[ContainsMethod, FunctionT]):  # noqa: D101
    method: str

    @override
    def prepare_request(self, request: ContainsMethod, _arguments: BoundArguments) -> None:  # noqa: D102
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
class QueryParam(ParameterMarker[ContainsQueryParams]):
    """
    Mark parameter as a query parameter.

    Examples:
        >>> def call(query: Annotated[str, QueryParam("query")]) -> ...:
        >>>     ...
    """

    name: str

    @override
    def __call__(self, request: ContainsQueryParams, value: Any) -> None:  # noqa: D102
        request.query_params.append((self.name, value.value if isinstance(value, Enum) else value))


if not TYPE_CHECKING:

    @dataclass(**SLOTS)
    class Payload(ParameterMarker[ContainsPayload]):
        """
        Mark parameter as a request payload. An argument gets converted to a dictionary and passed over to a backend.

        Examples:
            Simple usage:

            >>> def call(body: Payload[BodyModel]) -> ...:
            >>>     ...

            Equivalent expanded usage:

            >>> def call(body: Annotated[BodyModel, Payload()]) -> ...:
            >>>     ...
        """

        exclude_unset: bool = False
        by_alias: bool = False

        @override
        def __call__(self, request: ContainsPayload, value: Any) -> None:  # noqa: D102
            value = get_type_adapter(type(value)).dump_python(
                value,
                by_alias=self.by_alias,
                exclude_unset=self.exclude_unset,
            )
            if request.payload is None:
                request.payload = value
            elif isinstance(request.payload, dict):
                request.payload.update(value)  # merge into the existing payload
            else:
                raise ValueError(f"attempting to merge {type(value)} into {type(request.payload)}")

        def __class_getitem__(cls, item: type[Any]) -> Any:
            return Annotated[item, cls()]

else:
    # Abandon hope all ye who enter here 👋
    #
    # Mypy still does not support `__class_getitem__`, although it was introduced in Python 3.7:
    # https://github.com/python/mypy/issues/11501.
    # This line allows to treat `Payload[T]` simply as `T` itself, that is consistent
    # with `Annotated[T, Payload()]` annotation.
    Payload: TypeAlias = _T


@dataclass(**SLOTS)
class Field(ParameterMarker[ContainsPayload]):
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
    def __call__(self, request: ContainsPayload, value: Any) -> None:  # noqa: D102
        if request.payload is None:
            request.payload = {}
        request.payload[self.name] = value.value if isinstance(value, Enum) else value


if not TYPE_CHECKING:

    @dataclass(**SLOTS)
    class FormData(ParameterMarker[ContainsFormData]):
        """
        Mark parameter as a request form data.

        An argument gets converted to a dictionary and passed over to a backend.

        Examples:
            >>> def call(body: FormData[FormModel]) -> ...:
            >>>     ...

            >>> def call(body: Annotated[FormModel, FormData()]) -> ...:
            >>>     ...
        """

        @override
        def __call__(self, request: ContainsFormData, value: Any) -> None:  # noqa: D102
            value = get_type_adapter(type(value)).dump_python(value, by_alias=True)
            if not isinstance(value, dict):
                raise TypeError(f"form data requires a dictionary, got {type(value)}")
            for item_name, item_value in value.items():
                request.append_form_field(item_name, item_value)

        def __class_getitem__(cls, item: type[Any]) -> Any:
            return Annotated[item, FormData()]

else:
    FormData: TypeAlias = _T


@dataclass(**SLOTS)
class FormField(ParameterMarker[ContainsFormData]):
    """
    Mark a parameter as a separate form field value.

    Examples:
        >>> def call(param: Annotated[int, FormField("param")]) -> ...:
        >>>     ...

    Notes:
        - Multiple arguments with the same field name are allowed
        - [`FormData`][combadge.support.http.markers.FormData] marker's fields get merged with `FormField` ones (if present)
        - Enum values are passed by value
    """  # noqa: E501

    name: str

    @override
    def __call__(self, request: ContainsFormData, value: Any) -> None:  # noqa: D102
        request.append_form_field(self.name, value.value if isinstance(value, Enum) else value)
