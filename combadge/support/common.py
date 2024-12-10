from typing import Annotated, TypeAlias

from pydantic import WrapValidator, Field
from typing import Any, TypedDict

from pydantic import ValidatorFunctionWrapHandler
from typing_extensions import ReadOnly

from combadge.core.typevars import AnyType


class BodySpecification(TypedDict):
    """Shared mixin that carries request or response body for a variety of application protocols."""

    body: ReadOnly[Any]
    """
    Request or response body.

    Note:
        This is an intermediate value in native Python types, which is not yet parsed or validated.
    """


def _validate_body(value: Any, handler: ValidatorFunctionWrapHandler) -> Any:
    """
    Delegate validation to the `body` value validator.

    Note:
        This is only needed because Pydantic does not handle `validation_alias` in `TypeAdapter`
        nor in `RootModel`. So, user would not be able to do `-> Annotated[..., Field(validation_alias="body")]`
        for primitive types.
    """
    try:
        body = value["body"]
    except KeyError as e:
        raise ValueError("`Body[...]` annotation is only applicable at the root level") from e
    else:
        return handler(body, "body")


Body: TypeAlias = Annotated[AnyType, Field(serialization_alias="body"), WrapValidator(_validate_body)]
"""
# As parameter type

Define request body as the argument value.

Examples:
    >>> # TODO

# As return type

Parse the given model from response body.

Examples:
    >>> class SupportsWttrIn(Protocol):
    >>>     @http_method("GET")
    >>>     @path("/{in_}")
    >>>     def get_weather(self, *, in_: str) -> Body[Weather]: ...
"""
