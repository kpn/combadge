"""
Mixins for HTTP-related request and response classes.

There are two types of mixins:

- Containers, named as `Contains*`, are data classes that actually store something.
- Protocols, named as `Protocol*`, are interfaces that should be implemented by the child classes.
"""

from abc import ABC
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol, Tuple


@dataclass
class ContainsHeaders(ABC):
    """HTTP request headers."""

    headers: List[Tuple[str, Any]] = field(default_factory=list)


@dataclass
class ContainsUrlPath(ABC):
    """Request URL path."""

    url_path: Optional[str] = None

    def get_url_path(self) -> str:
        """Get validated URL path."""
        if not (url_path := self.url_path):
            raise ValueError("an HTTP request requires a non-empty URL path")
        return url_path


@dataclass
class ContainsMethod(ABC):
    """HTTP request method."""

    method: Optional[str] = None

    def get_method(self) -> str:
        """Get a validated HTTP method."""
        if not (method := self.method):
            raise ValueError("an HTTP request requires a non-empty method")
        return method


@dataclass
class ContainsQueryParams(ABC):
    """HTTP request query parameters."""

    query_params: List[Tuple[str, Any]] = field(default_factory=list)


@dataclass
class ContainsFormData(ABC):
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
class ContainsPayload(ABC):
    """SOAP request payload."""

    payload: Optional[dict] = None

    def ensure_payload(self) -> dict:
        """Ensure that the payload is initialized and return it."""
        if self.payload is None:
            self.payload = {}
        return self.payload


class SupportsStatusCode(Protocol):
    """Supports a read-only status code attribute or property."""

    @property
    def status_code(self) -> int:  # noqa: D102
        raise NotImplementedError


class SupportsReasonPhrase(Protocol):
    """Supports a read-only reason phrase attribute or property."""

    @property
    def reason_phrase(self) -> str:  # noqa: D102
        raise NotImplementedError


class SupportsText(Protocol):
    """Supports a read-only text attribute or property."""

    @property
    def text(self) -> str:  # noqa: D102
        raise NotImplementedError
