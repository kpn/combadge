from typing import Annotated, Any, TypeAlias, TypedDict

from pydantic import ValidatorFunctionWrapHandler, WrapValidator
from typing_extensions import ReadOnly

from combadge.core.typevars import AnyType


class ResponseBodyMixinDict(TypedDict):
    """Shared mixin that carries response body for a variety of application protocols."""

    body: ReadOnly[Any]
    """
    Parsed response body.

    Note:
        This is an intermediate value, which is parsed into native Python types,
        but not yet validated into a final response model.
    """


def _validate_body(value: Any, handler: ValidatorFunctionWrapHandler) -> Any:
    try:
        body = value["body"]
    except KeyError as e:
        raise ValueError("`Body[...]` annotation is only applicable at the root level") from e
    else:
        return handler(body)


Body: TypeAlias = Annotated[AnyType, WrapValidator(_validate_body)]
"""
Shortcut to simplify protocol definition when a return model should be parsed from a response body.

It extracts the `"body"` value from
[`ResponseBodyMixinDict`][combadge.support.common.response.ResponseBodyMixinDict]
and forwards it to the model validator.

Examples:
    >>> class SupportsWttrIn(Protocol):
    >>>     @http_method("GET")
    >>>     @path("/{in_}")
    >>>     def get_weather(self, *, in_: str) -> Body[Weather]: ...
"""
