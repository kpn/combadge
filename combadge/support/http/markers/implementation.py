"""
Marker implementations.

Tip:
    It is advised to use the type aliases unless you really need to customize the behavior.
"""

from dataclasses import dataclass
from enum import Enum
from inspect import BoundArguments
from typing import Any, Callable, Generic, Union

from pydantic import BaseModel

from combadge.core.markers.method import MethodMarker
from combadge.core.markers.parameter import ParameterMarker
from combadge.core.typevars import FunctionT
from combadge.support.http.abc import (
    SupportsFormData,
    SupportsHeaders,
    SupportsJson,
    SupportsMethod,
    SupportsQueryParams,
    SupportsUrlPath,
)


@dataclass
class CustomHeader(ParameterMarker[SupportsHeaders]):
    """[`CustomHeader`][combadge.support.http.markers.CustomHeader] marker implementation."""

    name: str
    __slots__ = ("name",)

    def prepare_request(self, request: SupportsHeaders, value: Any) -> None:  # noqa: D102
        request.headers.append((self.name, value))


class Path(Generic[FunctionT], MethodMarker[SupportsUrlPath, FunctionT]):
    """[`path`][combadge.support.http.markers.path] marker implementation."""

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

    def prepare_request(self, request: SupportsUrlPath, arguments: BoundArguments) -> None:  # noqa: D102
        request.url_path = self._factory(arguments)


@dataclass
class HttpMethod(Generic[FunctionT], MethodMarker[SupportsMethod, FunctionT]):
    """[`http_method`][combadge.support.http.markers.http_method] marker implementation."""

    method: str

    def prepare_request(self, request: SupportsMethod, _arguments: BoundArguments) -> None:  # noqa: D102
        request.method = self.method


@dataclass
class QueryParam(ParameterMarker[SupportsQueryParams]):
    """[`QueryParam`][combadge.support.http.markers.QueryParam] marker implementation."""

    name: str
    __slots__ = ("name",)

    def prepare_request(self, request: SupportsQueryParams, value: Any) -> None:  # noqa: D102
        request.query_params.append((self.name, value.value if isinstance(value, Enum) else value))


@dataclass
class Json(ParameterMarker[SupportsJson]):
    """
    [`Json`][combadge.support.http.markers.Json] marker implementation.

    Used for a more complex annotations, for example:

    ```python
    Annotated[BodyModel, Json(), AnotherMarker]
    ```
    """

    exclude_unset: bool = False
    by_alias: bool = False

    def prepare_request(self, request: SupportsJson, value: BaseModel) -> None:  # noqa: D102
        request.json_.update(value.model_dump(by_alias=self.by_alias, exclude_unset=self.exclude_unset))


@dataclass
class JsonField(ParameterMarker[SupportsJson]):
    """
    [`JsonField`][combadge.support.http.markers.JsonField] implementation.

    It's recommended that you use the alias, unless you need a complex annotation, such as:

    ```python
    parameter: Annotated[int, JsonField("param"), AnotherMarker()]
    ```

    Notes:
        - Enum values are passed by value
    """

    name: str
    __slots__ = ("name",)

    def prepare_request(self, request: SupportsJson, value: Any) -> None:  # noqa: D102
        request.json_[self.name] = value.value if isinstance(value, Enum) else value


@dataclass
class FormData(ParameterMarker[SupportsFormData]):
    """
    [`FormData`][combadge.support.http.markers.FormData] implementation.

    Used for a more complex annotations, for example:

    ```python
    Annotated[BodyModel, FormData(), AnotherMarker]
    ```
    """

    __slots__ = ()

    def prepare_request(self, request: SupportsFormData, value: BaseModel) -> None:  # noqa: D102
        for item_name, item_value in value.model_dump(by_alias=True).items():
            request.append_form_field(item_name, item_value)


@dataclass
class FormField(ParameterMarker[SupportsFormData]):
    """
    [`FormField`][combadge.support.http.markers.FormField] marker implementation.

    It's recommended that you use the alias, unless you need a complex annotation, such as:

    ```python
    parameter: Annotated[int, FormField("param"), AnotherMarker()]
    ```

    Notes:
        - Enum values are passed by value
    """

    name: str
    __slots__ = ("name",)

    def prepare_request(self, request: SupportsFormData, value: Any) -> None:  # noqa: D102
        request.append_form_field(self.name, value.value if isinstance(value, Enum) else value)
