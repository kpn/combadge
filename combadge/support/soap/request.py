from pydantic import BaseModel

from combadge.support.abc import RequiresBody, RequiresOperationName


class Request(RequiresOperationName, RequiresBody, BaseModel):
    """Backend-agnostic SOAP request."""
