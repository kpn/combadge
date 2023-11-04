from __future__ import annotations

from dataclasses import dataclass
from http import HTTPStatus
from typing import Any, MutableMapping, TypeVar

from typing_extensions import Annotated, TypeAlias

from combadge.core.markers.response import Drop, GetItem, ResponseMarker
from combadge.support.http.abc import SupportsReasonPhrase, SupportsStatusCode, SupportsText

_MutableMappingT = TypeVar("_MutableMappingT", bound=MutableMapping[Any, Any])


@dataclass
class StatusCodeMixin(ResponseMarker):
    """
    Update payload with response status code.

    Warning:
        Input payload **must be** a mutable mapping (for example, a `#!python dict`).
        If this is not the case, map it first with the [`Map` marker][combadge.core.markers.response.Map].
    """

    key: Any = "status_code"
    """Key under which the status code should assigned in the payload."""

    def transform(self, response: SupportsStatusCode, input_: _MutableMappingT) -> _MutableMappingT:  # noqa: D102
        input_[self.key] = HTTPStatus(response.status_code)
        return input_


@dataclass
class ReasonPhraseMixin(ResponseMarker):
    """Update payload with HTTP reason message."""

    key: Any = "reason"
    """Key under which the reason message should assigned in the payload."""

    def transform(self, response: SupportsReasonPhrase, input_: _MutableMappingT) -> _MutableMappingT:  # noqa: D102
        input_[self.key] = response.reason_phrase
        return input_


@dataclass
class TextMixin(ResponseMarker):
    """
    Update payload with HTTP response text.

    Examples:
        >>> class MyResponse(BaseModel):
        >>>     my_text: str
        >>>
        >>> class MyService(Protocol):
        >>>     @http_method("GET")
        >>>     @path(...)
        >>>     def get_text(self) -> Annotated[MyResponse, TextMixin("my_text")]:
        >>>         ...
    """

    key: Any = "text"
    """Key under which the text contents should assigned in the payload."""

    def transform(self, response: SupportsText, input_: _MutableMappingT) -> _MutableMappingT:  # noqa: D102
        input_[self.key] = response.text
        return input_


StatusCode: TypeAlias = Annotated[HTTPStatus, Drop(), StatusCodeMixin(), GetItem("status_code")]
"""
Shortcut to retrieve just a response status code.

Examples:
    >>> def call(...) -> StatusCode:
    >>>     ...
"""


__all__ = ("StatusCodeMixin", "ReasonPhraseMixin", "TextMixin", "StatusCode")
