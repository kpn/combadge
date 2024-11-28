from __future__ import annotations

from dataclasses import dataclass
from http import HTTPStatus
from typing import Any

from typing_extensions import override

from combadge._helpers.dataclasses import SLOTS
from combadge.core.markers.response import ResponseMarker
from combadge.support.http.abc import (
    HttpResponseHeaders,
    HttpResponseReasonPhrase,
    HttpResponseStatusCode,
    HttpResponseText,
)


@dataclass(frozen=True, **SLOTS)
class StatusCode(ResponseMarker):
    """
    Enrich the payload with response status code.

    Examples:
        >>> def call(...) -> Annotated[Model, Mixin(StatusCode())]:
        >>>     ...
    """

    key: Any = "status_code"
    """Key under which the status code should mapped in the payload."""

    @override
    def __call__(self, response: HttpResponseStatusCode, payload: Any) -> dict[Any, Any]:  # noqa: D102
        return {self.key: HTTPStatus(response.status_code)}


@dataclass(frozen=True, **SLOTS)
class ReasonPhrase(ResponseMarker):
    """Enrich the payload with HTTP reason message."""

    key: Any = "reason"
    """Key under which the reason message should mapped in the payload."""

    @override
    def __call__(self, response: HttpResponseReasonPhrase, payload: Any) -> dict[Any, Any]:  # noqa: D102
        return {self.key: response.reason_phrase}


@dataclass(frozen=True, **SLOTS)
class Text(ResponseMarker):
    """
    Enrich the payload with HTTP response text.

    Examples:
        >>> class MyResponse(BaseModel):
        >>>     my_text: str
        >>>
        >>> class MyService(Protocol):
        >>>     @http_method("GET")
        >>>     @path(...)
        >>>     def get_text(self) -> Annotated[MyResponse, Text("my_text")]:
        >>>         ...
    """

    key: Any = "text"
    """Key under which the text contents should assigned in the payload."""

    @override
    def __call__(self, response: HttpResponseText, payload: Any) -> dict[Any, Any]:  # noqa: D102
        return {self.key: response.text}


@dataclass(frozen=True, **SLOTS)
class Header(ResponseMarker):
    """
    Enrich the payload with the specified HTTP header's value.

    If the header be missing, the payload will not be enriched.

    Examples:
        >>> class MyResponse(BaseModel):
        >>>     content_length: int
        >>>     optional: str = "default"
        >>>
        >>> class MyService(Protocol):
        >>>     @http_method("GET")
        >>>     @path(...)
        >>>     def get_something(self) -> Annotated[
        >>>         MyResponse,
        >>>         Header(header="content-length", key="content_length"),
        >>>         Header(header="x-optional", key="optional"),
        >>>     ]:
        >>>         ...
    """

    header: str
    """HTTP header name, case-insensitive."""

    key: Any
    """Key under which the header contents should assigned in the payload."""

    @override
    def __call__(self, response: HttpResponseHeaders, payload: Any) -> dict[Any, Any]:  # noqa: D102
        try:
            value = response.headers[self.header]
        except KeyError:
            return {}
        else:
            return {self.key: value}


__all__ = ("StatusCode", "ReasonPhrase", "Text", "Header")
