"""Mixins for HTTP-related request and response classes."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class ContainsHeaders:
    """HTTP request headers."""

    headers: List[Tuple[str, Any]] = field(default_factory=list)


@dataclass
class ContainsUrlPath:
    """Request URL path."""

    url_path: Optional[str] = None

    def get_url_path(self) -> str:
        """Get validated URL path."""
        if not (url_path := self.url_path):
            raise ValueError("an HTTP request requires a non-empty URL path")
        return url_path


@dataclass
class ContainsMethod:
    """HTTP request method."""

    method: Optional[str] = None

    def get_method(self) -> str:
        """Get a validated HTTP method."""
        if not (method := self.method):
            raise ValueError("an HTTP request requires a non-empty method")
        return method


@dataclass
class ContainsQueryParams:
    """HTTP request query parameters."""

    query_params: List[Tuple[str, Any]] = field(default_factory=list)


@dataclass
class ContainsFormData:
    """
    HTTP request [form data][1].

    [1]: https://developer.mozilla.org/en-US/docs/Learn/Forms/Sending_and_retrieving_form_data
    """

    form_data: Dict[str, List[Any]] = field(default_factory=dict)
    """
    Used with [FormData][combadge.support.http.markers.FormData]
    and [FormField][combadge.support.http.markers.FormField].
    """

    def append_form_field(self, name: str, value: Any) -> None:  # noqa: D102
        self.form_data.setdefault(name, []).append(value)


@dataclass
class ContainsPayload:
    """SOAP request payload."""

    payload: Optional[Any] = None
