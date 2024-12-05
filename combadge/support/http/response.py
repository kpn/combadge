"""HTTP backend response dictionaries."""

from collections.abc import Mapping
from http import HTTPStatus
from typing import Generic, TypedDict

from typing_extensions import ReadOnly, TypeVar


class HttpResponseDict(TypedDict):
    """HTTP-specific values."""

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
