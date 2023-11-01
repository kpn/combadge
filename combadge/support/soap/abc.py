from abc import ABC
from dataclasses import dataclass
from typing import Optional


@dataclass
class SupportsOperationName(ABC):
    """SOAP operation name."""

    operation_name: Optional[str] = None

    def get_operation_name(self) -> str:
        """Get validated SOAP operation name."""
        if not (operation_name := self.operation_name):
            raise ValueError("a SOAP request requires a non-empty operation name")
        return operation_name


@dataclass
class SupportsBody(ABC):
    """SOAP request body."""

    body: Optional[dict] = None

    def get_body(self) -> dict:
        """Get a validated request body."""
        if (body := self.body) is None:
            raise ValueError("a SOAP request requires a non-empty body")
        return body
