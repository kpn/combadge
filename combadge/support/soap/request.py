from combadge.core.request import BaseRequest
from combadge.support.soap.abc import RequiresBody, RequiresOperationName


class Request(RequiresOperationName, RequiresBody, BaseRequest):
    """Backend-agnostic SOAP request."""
