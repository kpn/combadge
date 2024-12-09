from typing import Annotated, TypeAlias

from pydantic import Field, WrapValidator

from combadge.core.typevars import AnyType
from combadge.support.common.response import _validate_body

Body: TypeAlias = Annotated[AnyType, Field(serialization_alias="body"), WrapValidator(_validate_body)]
"""
# Parameter type

Sets the request body to the argument value.

Examples:
    >>> # TODO

# Return type

Parse the given model from response body.

Examples:
    >>> class SupportsWttrIn(Protocol):
    >>>     @http_method("GET")
    >>>     @path("/{in_}")
    >>>     def get_weather(self, *, in_: str) -> Body[Weather]: ...
"""
