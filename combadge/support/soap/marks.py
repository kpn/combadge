"""Mixins for SOAP request classes."""

from dataclasses import dataclass
from typing import Any, Dict, Tuple

from combadge.core.mark import MethodMark
from combadge.core.typevars import Identity
from combadge.support.soap.abc import RequiresOperationName


@dataclass
class _OperationNameMethodMark(MethodMark[RequiresOperationName]):
    name: str

    __slots__ = ("name",)

    def prepare_request(  # noqa: D102
        self,
        request: RequiresOperationName,
        _args: Tuple[Any, ...],
        _kwargs: Dict[str, Any],
    ) -> None:
        request.operation_name = self.name


def operation_name(name: str) -> Identity:
    """Designates a service call's operation name (for example, SOAP name)."""
    return _OperationNameMethodMark(name).mark
