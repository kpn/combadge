"""HTTP backend response dictionaries."""

from collections.abc import Mapping
from http import HTTPStatus
from typing import Annotated, Final, Generic, TypedDict

from pydantic import AliasPath, Field
from typing_extensions import ReadOnly, TypeAlias, TypeVar


class HttpResponseDict(TypedDict):
    """HTTP-specific values."""

    status: ReadOnly[HTTPStatus]
    """HTTP response status."""

    reason: ReadOnly[str]
    """HTTP response reason text."""

    headers: ReadOnly[Mapping[str, str]]
    """HTTP response headers."""


_HttpDictT = TypeVar("_HttpDictT", default=HttpResponseDict)
"""Concrete type of the HTTP sub-key value."""


class HttpResponseMixinDict(TypedDict, Generic[_HttpDictT]):
    """HTTP-specific values."""

    http: ReadOnly[_HttpDictT]
    """HTTP-specific values."""


HTTP_REASON_PATH: Final[AliasPath] = AliasPath("http", "reason")
"""Alias path to HTTP response reason phrase."""

HttpReason: TypeAlias = Annotated[str, Field(validation_alias=HTTP_REASON_PATH)]
"""Type alias for HTTP response reason phrase."""

HTTP_STATUS_PATH: Final[AliasPath] = AliasPath("http", "status")
"""Alias path to HTTP response status code."""

HttpStatus: TypeAlias = Annotated[HTTPStatus, Field(validation_alias=HTTP_STATUS_PATH)]
"""Type alias for HTTP response status code"""

HTTP_HEADERS_PATH: Final[AliasPath] = AliasPath("http", "headers")
"""Alias path to HTTP response headers."""

HttpHeaders: TypeAlias = Annotated[Mapping[str, str], Field(validation_alias=HTTP_HEADERS_PATH)]
"""Type alias for HTTP headers."""
