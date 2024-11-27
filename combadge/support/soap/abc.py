from dataclasses import dataclass
from typing import Any, Optional

from combadge._helpers.dataclasses import SLOTS


@dataclass(**SLOTS)
class ContainsSoapOperationName:
    """SOAP operation name."""

    operation_name: Optional[str] = None

    def get_operation_name(self) -> str:
        """Get validated SOAP operation name."""
        if not (operation_name := self.operation_name):
            raise ValueError("a SOAP request requires a non-empty operation name")
        return operation_name


@dataclass
class ContainsSoapHeader:
    """SOAP request header."""

    soap_header: Optional[Any] = None
    """SOAP header payload."""
