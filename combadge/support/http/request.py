from dataclasses import dataclass

from combadge.support.http.abc import (
    ContainsFormData,
    ContainsHeaders,
    ContainsMethod,
    ContainsPayload,
    ContainsQueryParams,
    ContainsUrlPath,
)
from combadge.support.shared.request import BaseBackendRequest


@dataclass
class Request(
    ContainsMethod,
    ContainsUrlPath,
    ContainsPayload,
    ContainsQueryParams,
    ContainsFormData,
    ContainsHeaders,
    BaseBackendRequest,
):
    """Backend-agnostic HTTP request."""
