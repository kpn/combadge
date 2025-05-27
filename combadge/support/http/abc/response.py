"""Interfaces for HTTP-related request and response classes."""

from collections.abc import Mapping

from typing_extensions import Protocol


class HttpResponseHeaders(Protocol):
    """Supports read-only case-insensitive mapping of headers."""

    @property
    def headers(self) -> Mapping[str, str]:  # noqa: D102
        raise NotImplementedError


class HttpResponseStatusCode(Protocol):
    """Supports a read-only status code attribute or property."""

    @property
    def status_code(self) -> int:  # noqa: D102
        raise NotImplementedError


class HttpResponseReasonPhrase(Protocol):
    """Supports a read-only reason phrase attribute or property."""

    @property
    def reason_phrase(self) -> str:  # noqa: D102
        raise NotImplementedError


class HttpResponseText(Protocol):
    """Supports a read-only text attribute or property."""

    @property
    def text(self) -> str:  # noqa: D102
        """Get the response body as text."""
        raise NotImplementedError
