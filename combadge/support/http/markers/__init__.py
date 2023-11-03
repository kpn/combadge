"""
Marker implementations.

Tip:
    It is advised to use the type aliases unless you really need to customize the behavior.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from inspect import BoundArguments
from typing import Any, Callable, Generic

from pydantic import BaseModel

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


@dataclass
class CustomHeader(ParameterMarker[ContainsHeaders]):
    """
    Mark a parameter as a header value. Argument is passed «as is» during a service call.

    Examples:
        >>> class Service(Protocol):
        >>>     def service(self, accept_language: Annotated[str, CustomHeader("Accept-Language")]):
        >>>         ...
    """

    name: str
    __slots__ = ("name",)

    def prepare_request(self, request: ContainsHeaders, value: Any) -> None:  # noqa: D102
        request.headers.append((self.name, value))


class Path(Generic[FunctionT], MethodMarker[ContainsUrlPath, FunctionT]):
    """[`path`][combadge.support.http.markers.shortcuts.path] marker implementation."""

    _factory: Callable[[BoundArguments], str]
    __slots__ = ("_factory",)

    def __init__(self, path_or_factory: str | Callable[[BoundArguments], str]) -> None:  # noqa: D107
        if callable(path_or_factory):
            self._factory = path_or_factory
        else:

            def factory(arguments: BoundArguments) -> str:
                # The `arguments.arguments` will contain the positional arguments too.
                # This is intentional to allow referring to positional arguments by their indexes and names.
                return path_or_factory.format(*arguments.args, **arguments.arguments)  # type: ignore[union-attr]

            self._factory = factory

    def prepare_request(self, request: ContainsUrlPath, arguments: BoundArguments) -> None:  # noqa: D102
        request.url_path = self._factory(arguments)


@dataclass
class HttpMethod(Generic[FunctionT], MethodMarker[ContainsMethod, FunctionT]):
    """[`http_method`][combadge.support.http.markers.shortcuts.http_method] marker implementation."""

    method: str

    def prepare_request(self, request: ContainsMethod, _arguments: BoundArguments) -> None:  # noqa: D102
        request.method = self.method


@dataclass
class QueryParam(ParameterMarker[ContainsQueryParams]):
    """[`QueryParam`][combadge.support.http.markers.QueryParam] marker implementation."""

    name: str
    __slots__ = ("name",)

    def prepare_request(self, request: ContainsQueryParams, value: Any) -> None:  # noqa: D102
        request.query_params.append((self.name, value.value if isinstance(value, Enum) else value))


@dataclass
class Payload(ParameterMarker[ContainsPayload]):
    """
    [`Payload`][combadge.support.http.markers.Payload] marker implementation.

    Used for a more complex annotations, for example:

    ```python
    Annotated[BodyModel, Payload(), AnotherMarker]
    ```
    """

    exclude_unset: bool = False
    by_alias: bool = False

    def prepare_request(self, request: ContainsPayload, value: BaseModel) -> None:  # noqa: D102
        request.ensure_payload().update(value.model_dump(by_alias=self.by_alias, exclude_unset=self.exclude_unset))


@dataclass
class Field(ParameterMarker[ContainsPayload]):
    """
    Mark a parameter as a value of a separate payload field.

    Examples:
        >>> from combadge.support.http.markers.implementation import Field
        >>>
        >>> def call(param: Annotated[int, Field("param")]) -> ...:
        >>>     ...

    Notes:
        - Enum values are passed by value
    """

    name: str
    __slots__ = ("name",)

    def prepare_request(self, request: ContainsPayload, value: Any) -> None:  # noqa: D102
        request.ensure_payload()[self.name] = value.value if isinstance(value, Enum) else value


@dataclass
class FormData(ParameterMarker[ContainsFormData]):
    """
    [`FormData`][combadge.support.http.markers.FormData] implementation.

    Used for a more complex annotations, for example:

    ```python
    Annotated[BodyModel, FormData(), AnotherMarker]
    ```
    """

    __slots__ = ()

    def prepare_request(self, request: ContainsFormData, value: BaseModel) -> None:  # noqa: D102
        for item_name, item_value in value.model_dump(by_alias=True).items():
            request.append_form_field(item_name, item_value)


@dataclass
class FormField(ParameterMarker[ContainsFormData]):
    """
    Mark a parameter as a separate form field value.

    Examples:
        >>> from combadge.support.http.markers.implementation import FormField
        >>>
        >>> def call(param: Annotated[int, FormField("param")]) -> ...:
        >>>     ...

    Notes:
        - Multiple arguments with the same field name are allowed
        - [`FormData`][combadge.support.http.markers.FormData] marker's fields get merged with `FormField` ones (if present)
        - Enum values are passed by value
    """  # noqa: E501

    name: str
    __slots__ = ("name",)

    def prepare_request(self, request: ContainsFormData, value: Any) -> None:  # noqa: D102
        request.append_form_field(self.name, value.value if isinstance(value, Enum) else value)
