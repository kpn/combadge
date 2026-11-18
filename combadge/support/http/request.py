from dataclasses import dataclass

from combadge.support.http.abc import (
    HttpRequestFormData,
    HttpRequestHeaders,
    HttpRequestMethod,
    HttpRequestPayload,
    HttpRequestQueryParams,
    HttpRequestUrlPath,
)
from combadge.support.shared.request import BaseBackendRequest


@dataclass(slots=True)
class Request(
    BaseBackendRequest,
    HttpRequestFormData,
    HttpRequestHeaders,
    HttpRequestMethod,
    HttpRequestPayload,
    HttpRequestQueryParams,
    HttpRequestUrlPath,
):
    """Backend-agnostic HTTP request."""
