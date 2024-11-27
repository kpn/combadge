from dataclasses import dataclass

from combadge._helpers.dataclasses import SLOTS
from combadge.support.http.abc import ContainsPayload
from combadge.support.shared.request import BaseBackendRequest
from combadge.support.soap.abc import ContainsSoapHeader, ContainsSoapOperationName


@dataclass(**SLOTS)
class Request(ContainsSoapOperationName, ContainsSoapHeader, ContainsPayload, BaseBackendRequest):
    """Backend-agnostic SOAP request."""
