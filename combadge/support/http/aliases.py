from http import HTTPStatus
from typing import TypeVar

from pydantic import Field
from typing_extensions import Annotated, TypeAlias

_StatusCodeT = TypeVar("_StatusCodeT", bound=HTTPStatus)
STATUS_CODE_ALIAS = "__status_code__"
StatusCode: TypeAlias = Annotated[_StatusCodeT, Field(alias=STATUS_CODE_ALIAS)]

_ReasonT = TypeVar("_ReasonT", bound=str)
REASON_ALIAS = "__reason__"
Reason: TypeAlias = Annotated[_ReasonT, Field(alias=REASON_ALIAS)]
