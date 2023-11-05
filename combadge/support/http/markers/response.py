from __future__ import annotations

from dataclasses import dataclass
from http import HTTPStatus
from typing import Any, Dict

# noinspection PyUnresolvedReferences
from typing_extensions import override

from combadge.core.markers.response import ResponseMarker
from combadge.support.http.abc import SupportsReasonPhrase, SupportsStatusCode, SupportsText


@dataclass
class StatusCode(ResponseMarker):
    """Build a payload with response status code."""

    key: Any = "status_code"
    """Key under which the status code should mapped in the payload."""

    @override
    def __call__(self, response: SupportsStatusCode, input_: Any) -> Dict[Any, Any]:  # noqa: D102
        return {self.key: HTTPStatus(response.status_code)}


@dataclass
class ReasonPhrase(ResponseMarker):
    """Build a payload with HTTP reason message."""

    key: Any = "reason"
    """Key under which the reason message should mapped in the payload."""

    @override
    def __call__(self, response: SupportsReasonPhrase, input_: Any) -> Dict[Any, Any]:  # noqa: D102
        return {self.key: response.reason_phrase}


@dataclass
class Text(ResponseMarker):
    """
    Build a payload with HTTP response text.

    Examples:
        >>> class MyResponse(BaseModel):
        >>>     my_text: str
        >>>
        >>> class MyService(Protocol):
        >>>     @http_method("GET")
        >>>     @path(...)
        >>>     def get_text(self) -> Annotated[MyResponse, Text("my_text"), Extract("my_text")]:
        >>>         ...
    """

    key: Any = "text"
    """Key under which the text contents should assigned in the payload."""

    @override
    def __call__(self, response: SupportsText, input_: Any) -> Dict[Any, Any]:  # noqa: D102
        return {self.key: response.text}


__all__ = ("StatusCode", "ReasonPhrase", "Text")
