from dataclasses import dataclass

from annotated_types import SLOTS

from combadge.support.common.request import BaseBackendRequest
from combadge.support.http.abc import HttpRequestPayload
from combadge.support.soap.abc import SoapHeader, SoapOperationName


@dataclass(**SLOTS)
class Request(BaseBackendRequest, SoapOperationName, SoapHeader, HttpRequestPayload):
    """Backend-agnostic SOAP request."""
