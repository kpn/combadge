from __future__ import annotations

from dataclasses import dataclass
from http import HTTPStatus
from typing import Any, Dict

# noinspection PyUnresolvedReferences
from typing_extensions import override

from combadge._helpers.dataclasses import SLOTS
from combadge.core.markers.response import ResponseMarker
from combadge.support.http.abc import SupportsHeaders, SupportsReasonPhrase, SupportsStatusCode, SupportsText


@dataclass(**SLOTS)
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
    def __call__(self, response: SupportsStatusCode, payload: Any) -> Dict[Any, Any]:  # noqa: D102
        return {self.key: HTTPStatus(response.status_code)}


@dataclass(**SLOTS)
class ReasonPhrase(ResponseMarker):
    """Enrich the payload with HTTP reason message."""

    key: Any = "reason"
    """Key under which the reason message should mapped in the payload."""

    @override
    def __call__(self, response: SupportsReasonPhrase, payload: Any) -> Dict[Any, Any]:  # noqa: D102
        return {self.key: response.reason_phrase}


@dataclass(**SLOTS)
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
    def __call__(self, response: SupportsText, payload: Any) -> Dict[Any, Any]:  # noqa: D102
        return {self.key: response.text}


@dataclass(**SLOTS)
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
    def __call__(self, response: SupportsHeaders, payload: Any) -> Dict[Any, Any]:  # noqa: D102
        try:
            value = response.headers[self.header]
        except KeyError:
            return {}
        else:
            return {self.key: value}


__all__ = ("StatusCode", "ReasonPhrase", "Text", "Header")
