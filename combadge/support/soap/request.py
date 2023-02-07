from pydantic import BaseModel

from combadge.support.http.abc import RequiresBody
from combadge.support.soap.abc import RequiresOperationName


class Request(RequiresOperationName, RequiresBody, BaseModel):
    """Backend-agnostic SOAP request."""
