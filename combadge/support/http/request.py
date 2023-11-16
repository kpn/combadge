from dataclasses import dataclass

from combadge._helpers.dataclasses import SLOTS
from combadge.support.http.abc import (
    ContainsFormData,
    ContainsHeaders,
    ContainsMethod,
    ContainsPayload,
    ContainsQueryParams,
    ContainsUrlPath,
)
from combadge.support.shared.request import BaseBackendRequest


@dataclass(**SLOTS)
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
