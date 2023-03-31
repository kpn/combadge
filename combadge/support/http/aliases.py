from http import HTTPStatus
from typing import TypeVar

from pydantic import Field
from typing_extensions import Annotated, TypeAlias

_StatusCodeT = TypeVar("_StatusCodeT", bound=HTTPStatus)
STATUS_CODE_ALIAS = "__status_code__"
StatusCode: TypeAlias = Annotated[_StatusCodeT, Field(alias=STATUS_CODE_ALIAS)]
"""HTTP status code. Alias for the `__status_code__` pseudo-field."""

_ReasonT = TypeVar("_ReasonT", bound=str)
REASON_ALIAS = "__reason__"
Reason: TypeAlias = Annotated[_ReasonT, Field(alias=REASON_ALIAS)]
"""HTTP reason phrase. Alias for the `__reason__` pseudo-field."""

_ContentT = TypeVar("_ContentT", bound=bytes)
CONTENT_ALIAS = "__content__"
Content: TypeAlias = Annotated[_ContentT, Field(alias=CONTENT_ALIAS)]
"""Original response content. Alias for the `__content__` pseudo-field."""
