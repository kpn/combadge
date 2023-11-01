from dataclasses import dataclass

from combadge.support.http.abc import (
    SupportsFormData,
    SupportsHeaders,
    SupportsJson,
    SupportsMethod,
    SupportsQueryParams,
    SupportsUrlPath,
)
from combadge.support.shared.request import BaseBackendRequest


@dataclass
class Request(
    SupportsMethod,
    SupportsUrlPath,
    SupportsJson,
    SupportsQueryParams,
    SupportsFormData,
    SupportsHeaders,
    BaseBackendRequest,
):
    """Backend-agnostic HTTP request."""
