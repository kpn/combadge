from dataclasses import dataclass

from annotated_types import SLOTS

from combadge.support.http.abc import (
    HttpRequestFormData,
    HttpRequestHeaders,
    HttpRequestMethod,
    HttpRequestPayload,
    HttpRequestQueryParams,
    HttpRequestUrlPath,
)
from combadge.support.shared.request import BaseBackendRequest


@dataclass(**SLOTS)
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
