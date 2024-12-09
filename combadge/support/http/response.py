"""HTTP response types."""

from collections.abc import Mapping
from http import HTTPStatus
from typing import Annotated, Generic, TypeAlias, TypedDict

from pydantic import AliasPath, Field
from typing_extensions import ReadOnly, TypeVar


class HttpResponseDict(TypedDict):
    """
    HTTP-specific values under the `http` entry.

    This typed dictionary defines sane defaults for HTTP backends, but they are free to extend it
    and specify a concrete specification in the `HttpResponseMixinDict` generic parameter.
    """

    status: ReadOnly[HTTPStatus]
    """HTTP response status."""

    reason: ReadOnly[str]
    """HTTP response reason text."""

    headers: ReadOnly[Mapping[str, str]]
    """Raw HTTP response headers."""


_HttpDictT = TypeVar("_HttpDictT", default=HttpResponseDict)
"""Concrete type of the HTTP sub-key value."""


class HttpResponseMixinDict(TypedDict, Generic[_HttpDictT]):
    """HTTP-specific values."""

    http: ReadOnly[_HttpDictT]
    """HTTP-specific response values."""


Status: TypeAlias = Annotated[HTTPStatus, Field(validation_alias=AliasPath("http", "status"))]
"""
Shortcut for HTTP response status code.

Examples:
    >>> class Response(BaseModel):
    >>>     my_status_code: Status
"""

Reason: TypeAlias = Annotated[str, Field(validation_alias=AliasPath("http", "reason"))]
"""
Shortcut for HTTP reason phrase.

Examples:
    >>> class Response(BaseModel):
    >>>     reason_phrase: Reason
"""
