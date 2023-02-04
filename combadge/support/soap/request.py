from pydantic import BaseModel

from combadge.support.http.abc import RequiresBody, RequiresOperationName


class Request(RequiresOperationName, RequiresBody, BaseModel):
    """Backend-agnostic SOAP request."""
