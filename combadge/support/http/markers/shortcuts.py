"""Markers for HTTP-compatible protocols."""

from typing import Any, Callable, TypeVar, Union

from typing_extensions import Annotated, TypeAlias

from combadge.core.typevars import FunctionT

from . import FormData as FormDataImplementation
from . import HttpMethod, Path
from . import Payload as PayloadImplementation
from . import QueryParam as QueryParamImplementation

_T = TypeVar("_T")


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


Payload: TypeAlias = Annotated[_T, PayloadImplementation()]
"""
# When used as a parameter type

Mark parameter as a request payload. An argument gets converted to a dictionary and passed over to a backend.

Examples:
    >>> class BodyModel(BaseModel):
    >>>     ...
    >>>
    >>> def call(body: Payload[BodyModel]) -> ...:
    >>>     ...
"""


FormData: TypeAlias = Annotated[_T, FormDataImplementation()]
"""
Mark parameter as a request form data. An argument gets converted to a dictionary and passed over to a backend.

Examples:
    >>> class FormModel(BaseModel):
    >>>     ...
    >>>
    >>> def call(body: FormData[FormModel]) -> ...:
    >>>     ...
"""
