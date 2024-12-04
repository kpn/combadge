from dataclasses import dataclass

from annotated_types import SLOTS

from combadge.support.common.request import BaseBackendRequest
from combadge.support.http.abc import (
    HttpRequestFormData,
    HttpRequestHeaders,
    HttpRequestMethod,
    HttpRequestPayload,
    HttpRequestQueryParams,
    HttpRequestUrlPath,
)


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
