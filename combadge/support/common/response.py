from typing import Any, TypedDict

from pydantic import ValidatorFunctionWrapHandler
from typing_extensions import ReadOnly


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
        return handler(body)
