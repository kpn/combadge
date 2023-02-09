from pydantic import BaseModel

from combadge.support.http.abc import SupportsBody
from combadge.support.rest.abc import RequiresMethod, RequiresPath, SupportsQueryParams


class Request(RequiresMethod, RequiresPath, SupportsBody, SupportsQueryParams, BaseModel):
    """Backend-agnostic REST request."""
