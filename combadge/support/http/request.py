from pydantic import BaseModel

from combadge.support.http.abc import RequiresMethod, RequiresPath, SupportsFormData, SupportsJson, SupportsQueryParams


class Request(RequiresMethod, RequiresPath, SupportsJson, SupportsQueryParams, SupportsFormData, BaseModel):
    """Backend-agnostic REST request."""
