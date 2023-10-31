from combadge.core.request import BaseRequest
from combadge.support.http.abc import (
    RequiresMethod,
    RequiresPath,
    SupportsFormData,
    SupportsHeaders,
    SupportsJson,
    SupportsQueryParams,
)


class Request(
    RequiresMethod,
    RequiresPath,
    SupportsJson,
    SupportsQueryParams,
    SupportsFormData,
    SupportsHeaders,
    BaseRequest,
):
    """Backend-agnostic REST request."""
