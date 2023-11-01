from dataclasses import dataclass

from combadge.support.shared.request import BaseBackendRequest
from combadge.support.soap.abc import SupportsBody, SupportsOperationName


@dataclass
class Request(SupportsOperationName, SupportsBody, BaseBackendRequest):
    """Backend-agnostic SOAP request."""
