"""Mixins for HTTP-related request and response classes."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class HttpRequestHeaders:
    """HTTP request headers."""

    http_headers: list[tuple[str, Any]] = field(default_factory=list)


@dataclass
class HttpRequestUrlPath:
    """HTTP request URL path."""

    url_path: str | None = None

    def get_url_path(self) -> str:
        """Get validated URL path."""
        if not (url_path := self.url_path):
            raise ValueError("an HTTP request requires a non-empty URL path")
        return url_path


@dataclass
class HttpRequestMethod:
    """HTTP request method."""

    method: str | None = None

    def get_method(self) -> str:
        """Get a validated HTTP method."""
        if not (method := self.method):
            raise ValueError("an HTTP request requires a non-empty method")
        return method


@dataclass
class HttpRequestQueryParams:
    """HTTP request query parameters."""

    query_params: list[tuple[str, Any]] = field(default_factory=list)


@dataclass
class HttpRequestFormData:
    """
    HTTP request [form data][1].

    [1]: https://developer.mozilla.org/en-US/docs/Learn/Forms/Sending_and_retrieving_form_data
    """

    form_data: dict[str, list[Any]] = field(default_factory=dict)
    """
    Used with [FormData][combadge.support.http.markers.FormData]
    and [FormField][combadge.support.http.markers.FormField].
    """

    def append_form_field(self, name: str, value: Any) -> None:  # noqa: D102
        self.form_data.setdefault(name, []).append(value)


@dataclass
class HttpRequestPayload:
    """HTTP request payload."""

    payload: Any | None = None
