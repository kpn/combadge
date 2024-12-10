"""Specification of HTTP request and response intermediate representation."""

from __future__ import annotations

from typing import TypedDict, Generic, Union

from typing_extensions import TypeVar, ReadOnly

from combadge.support.http.response import HttpResponseSpecification

_HttpDictT = TypeVar("_HttpDictT", bound=Union[HttpRequestSpecification, HttpResponseSpecification])
"""Concrete type of the HTTP sub-key value."""


class HttpSpecification(TypedDict, Generic[_HttpDictT]):
    """HTTP-specific values."""

    http: ReadOnly[_HttpDictT]
    """HTTP-specific request or response values."""
