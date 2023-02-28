from pydantic import BaseModel

from combadge.support.soap.abc import RequiresBody, RequiresOperationName


class Request(RequiresOperationName, RequiresBody, BaseModel):
    """Backend-agnostic SOAP request."""
