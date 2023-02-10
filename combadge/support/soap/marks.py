"""Mixins for SOAP request classes."""

from dataclasses import dataclass
from typing import Any, Dict, Tuple

from combadge.core.mark import MethodMark, make_method_mark_decorator
from combadge.support.soap.abc import RequiresOperationName


@dataclass
class OperationNameMethodMark(MethodMark[RequiresOperationName]):
    """Designates a service call's operation name (for example, SOAP name)."""

    name: str

    __slots__ = ("name",)

    def prepare_request(  # noqa: D102
        self,
        request: RequiresOperationName,
        _args: Tuple[Any, ...],
        _kwargs: Dict[str, Any],
    ) -> None:
        request.operation_name = self.name


operation_name = make_method_mark_decorator(OperationNameMethodMark)
