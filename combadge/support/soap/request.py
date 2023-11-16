from dataclasses import dataclass

from combadge._helpers.dataclasses import SLOTS
from combadge.support.http.abc import ContainsPayload
from combadge.support.shared.request import BaseBackendRequest
from combadge.support.soap.abc import ContainsOperationName


@dataclass(**SLOTS)
class Request(ContainsOperationName, ContainsPayload, BaseBackendRequest):
    """Backend-agnostic SOAP request."""
