from pydantic import BaseModel

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
    BaseModel,
):
    """Backend-agnostic REST request."""
