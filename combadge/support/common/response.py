from typing import Annotated, Any, Final, TypeAlias, TypedDict

from pydantic import AliasPath, Field
from typing_extensions import ReadOnly

from combadge.core.typevars import AnyType


class ResponseBodyMixinDict(TypedDict):
    """Shared mixin that carries response body for a variety of application protocols."""

    body: ReadOnly[Any]
    """Response body parsed into Python type, but not into a final response model."""


BODY_PATH: Final[AliasPath] = AliasPath("body")


Body: TypeAlias = Annotated[AnyType, Field(validation_alias=BODY_PATH)]
"""Validate the model from the response body."""
