"""Markers for HTTP-compatible protocols."""

from typing import Any, Callable, TypeVar, Union

from typing_extensions import Annotated, TypeAlias

from combadge.core.typevars import FunctionT

from .implementation import CustomHeader as CustomHeaderImplementation
from .implementation import FormData as FormDataImplementation
from .implementation import FormField as FormFieldImplementation
from .implementation import HttpMethod, Path
from .implementation import Json as JsonImplementation
from .implementation import JsonField as JsonFieldImplementation
from .implementation import QueryParam as QueryParamImplementation

_T = TypeVar("_T")


CustomHeader: TypeAlias = CustomHeaderImplementation
"""
Mark a parameter as a header value. Argument is passed «as is» during a service call.

Examples:
    >>> class Service(Protocol):
    >>>     def service(self, accept_language: Annotated[str, CustomHeader("Accept-Language")]):
    >>>         ...
"""


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
    return Path[Any](path_or_factory).mark


def http_method(method: str) -> Callable[[FunctionT], FunctionT]:
    """Specify an HTTP method."""
    return HttpMethod[Any](method).mark


QueryParam: TypeAlias = QueryParamImplementation
"""
Mark a parameter as a query parameter.

Notes:
    - Multiple arguments with the same query parameter name are allowed
"""


Json: TypeAlias = Annotated[_T, JsonImplementation()]
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


JsonField: TypeAlias = JsonFieldImplementation
"""
Mark a parameter as a separate JSON field value.

Examples:
    >>> from combadge.support.rest.markers import JsonField
    >>>
    >>> def call(param: Annotated[int, JsonField("param")]) -> ...:
    >>>     ...
"""


FormData: TypeAlias = Annotated[_T, FormDataImplementation()]
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


FormField: TypeAlias = FormFieldImplementation
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
