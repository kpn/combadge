from dataclasses import dataclass
from typing import Any

from annotated_types import SLOTS


@dataclass(**SLOTS)
class SoapOperationName:
    """SOAP operation name."""

    operation_name: str | None = None

    def get_operation_name(self) -> str:
        """Get validated SOAP operation name."""
        if not (operation_name := self.operation_name):
            raise ValueError("a SOAP request requires a non-empty operation name")
        return operation_name


@dataclass
class SoapHeader:
    """SOAP request header."""

    soap_header: Any | None = None
    """SOAP header payload."""
