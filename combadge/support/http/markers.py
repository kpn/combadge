"""Markers for HTTP-compatible protocols."""

from dataclasses import dataclass
from enum import Enum
from inspect import BoundArguments
from typing import Any, Callable, Generic, TypeVar, Union

from pydantic import BaseModel
from typing_extensions import Annotated, TypeAlias

from combadge.core.markers.method import MethodMarker
from combadge.core.markers.parameter import ParameterMarker
from combadge.core.typevars import FunctionT
from combadge.support.http.abc import (
    RequiresMethod,
    RequiresPath,
    SupportsFormData,
    SupportsHeaders,
    SupportsJson,
    SupportsQueryParams,
)

_T = TypeVar("_T")


@dataclass
class HeaderMarker(ParameterMarker[SupportsHeaders]):
    """Marker class for the [`Header`][combadge.support.http.markers.Header] alias."""

    name: str
    __slots__ = ("name",)

    def prepare_request(self, request: SupportsHeaders, value: Any) -> None:  # noqa: D102
        request.headers.append((self.name, value))


Header: TypeAlias = HeaderMarker
"""Mark a parameter as a header value."""


class _PathMarker(Generic[FunctionT], MethodMarker[RequiresPath, FunctionT]):
    _factory: Callable[[BoundArguments], str]
    __slots__ = ("_factory",)

    def __init__(self, path_or_factory: Union[str, Callable[[BoundArguments], str]]) -> None:  # noqa: D107
        if callable(path_or_factory):
            self._factory = path_or_factory
        else:

            def factory(arguments: BoundArguments) -> str:
                # The `arguments.arguments` will contain the positional arguments too.
                # This is intentional to allow referring to positional arguments by their indexes and names.
                return path_or_factory.format(*arguments.args, **arguments.arguments)  # type: ignore[union-attr]

            self._factory = factory

    def prepare_request(self, request: RequiresPath, arguments: BoundArguments) -> None:  # noqa: D102
        request.path = self._factory(arguments)


def path(path_or_factory: Union[str, Callable[..., str]]) -> Callable[[FunctionT], FunctionT]:
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
    return _PathMarker[Any](path_or_factory).mark


@dataclass
class _HttpMethodMarker(Generic[FunctionT], MethodMarker[RequiresMethod, FunctionT]):
    method: str

    def prepare_request(self, request: RequiresMethod, _arguments: BoundArguments) -> None:  # noqa: D102
        request.method = self.method


def http_method(method: str) -> Callable[[FunctionT], FunctionT]:
    """Specify an HTTP method."""
    return _HttpMethodMarker[Any](method).mark


@dataclass
class QueryMarker(ParameterMarker[SupportsQueryParams]):
    """Marker class for the [`QueryParam`][combadge.support.http.markers.QueryParam] alias."""

    name: str
    __slots__ = ("name",)

    def prepare_request(self, request: SupportsQueryParams, value: Any) -> None:  # noqa: D102
        request.query_params.append((self.name, value.value if isinstance(value, Enum) else value))


QueryParam: TypeAlias = QueryMarker
"""
Mark a parameter as a query parameter.

Notes:

    - Multiple arguments with the same query parameter name are allowed
"""


@dataclass
class JsonMarker(ParameterMarker[SupportsJson]):
    """
    Marker class for the [`Json`][combadge.support.http.markers.Json] alias.

    Used for a more complex annotations, for example:

    ```python
    Annotated[BodyModel, JsonParameterMarker(), AnotherMarker]
    ```
    """

    exclude_unset: bool = False
    by_alias: bool = False

    def prepare_request(self, request: SupportsJson, value: BaseModel) -> None:  # noqa: D102
        request.json_.update(value.dict(by_alias=self.by_alias, exclude_unset=self.exclude_unset))


Json: TypeAlias = Annotated[_T, JsonMarker()]
"""
Mark parameter as a request JSON body. An argument gets converted to a dictionary and passed over to a backend.

Examples:
    >>> from combadge.support.rest.markers import Json
    >>>
    >>> class BodyModel(BaseModel):
    >>>     ...
    >>>
    >>> def call(body: Json[BodyModel]) -> ...:
    >>>     ...
"""


@dataclass
class JsonFieldMarker(ParameterMarker[SupportsJson]):
    """
    Marker class for the [`JsonField`][combadge.support.http.markers.JsonField] alias.

    It's recommended that you use the alias, unless you need a complex annotation, such as:

    ```python
    parameter: Annotated[int, JsonFieldParameterMarker("param"), AnotherMarker()]
    ```

    Notes:
        - Enum values are passed by value
    """

    name: str
    __slots__ = ("name",)

    def prepare_request(self, request: SupportsJson, value: Any) -> None:  # noqa: D102
        request.json_[self.name] = value.value if isinstance(value, Enum) else value


JsonField: TypeAlias = JsonFieldMarker
"""
Mark a parameter as a separate JSON field value.

Examples:
    >>> from combadge.support.rest.markers import JsonField
    >>>
    >>> def call(param: Annotated[int, JsonField("param")]) -> ...:
    >>>     ...
"""


@dataclass
class FormDataMarker(ParameterMarker[SupportsFormData]):
    """
    Marker class for the [`FormData`][combadge.support.http.markers.FormData] alias.

    Used for a more complex annotations, for example:

    ```python
    Annotated[BodyModel, FormDataParameterMarker(), AnotherMarker]
    ```
    """

    __slots__ = ()

    def prepare_request(self, request: SupportsFormData, value: BaseModel) -> None:  # noqa: D102
        for item_name, item_value in value.dict(by_alias=True).items():
            request.append_form_field(item_name, item_value)


FormData: TypeAlias = Annotated[_T, FormDataMarker()]
"""
Mark parameter as a request form data. An argument gets converted to a dictionary and passed over to a backend.

Examples:
    >>> from combadge.support.rest.markers import FormData
    >>>
    >>> class FormModel(BaseModel):
    >>>     ...
    >>>
    >>> def call(body: FormData[FormModel]) -> ...:
    >>>     ...
"""


@dataclass
class FormFieldMarker(ParameterMarker[SupportsFormData]):
    """
    Marker class for the [`FormField`][combadge.support.http.markers.FormField] alias.

    It's recommended that you use the alias, unless you need a complex annotation, such as:

    ```python
    parameter: Annotated[int, FormFieldParameterMarker("param"), AnotherMarker()]
    ```

    Notes:
        - Enum values are passed by value
    """

    name: str
    __slots__ = ("name",)

    def prepare_request(self, request: SupportsFormData, value: Any) -> None:  # noqa: D102
        request.append_form_field(self.name, value.value if isinstance(value, Enum) else value)


FormField: TypeAlias = FormFieldMarker
"""
Mark a parameter as a separate form field value.

Examples:
    >>> from combadge.support.rest.markers import JsonField
    >>>
    >>> def call(param: Annotated[int, FormField("param")]) -> ...:
    >>>     ...

Notes:
    - Multiple arguments with the same field name are allowed
    - [`FormData`][combadge.support.http.markers.FormData] marker's fields get merged with `FormField` ones (if present)
"""
