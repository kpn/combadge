from dataclasses import dataclass

from combadge._helpers.dataclasses import SLOTS
from combadge.support.http.abc import (
    ContainsFormData,
    ContainsHttpHeaders,
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
    ContainsHttpHeaders,
    BaseBackendRequest,
):
    """Backend-agnostic HTTP request."""
