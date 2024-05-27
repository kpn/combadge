from dataclasses import dataclass
from typing import Optional

from combadge._helpers.dataclasses import SLOTS


@dataclass(**SLOTS)
class ContainsOperationName:
    """SOAP operation name."""

    operation_name: Optional[str] = None

    def get_operation_name(self) -> str:
        """Get validated SOAP operation name."""
        if not (operation_name := self.operation_name):
            raise ValueError("a SOAP request requires a non-empty operation name")
        return operation_name
