from pydantic import BaseModel

from combadge.support.http.abc import RequiresPath


class Request(RequiresPath, BaseModel):
    """Backend-agnostic HTTP request."""

    ...
