from dataclasses import dataclass

from combadge._helpers.dataclasses import SLOTS
from combadge.support.http.abc import HttpRequestPayload
from combadge.support.shared.request import BaseBackendRequest
from combadge.support.soap.abc import SoapHeader, SoapOperationName


@dataclass(**SLOTS)
class Request(BaseBackendRequest, SoapOperationName, SoapHeader, HttpRequestPayload):
    """Backend-agnostic SOAP request."""
