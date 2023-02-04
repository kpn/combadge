from dataclasses import dataclass
from typing import Any, Dict

from combadge.core.mark import MethodMark, make_method_mark_decorator
from combadge.support.http.abc import RequiresOperationName


@dataclass
class OperationNameMethodMark(MethodMark):
    """Designates a service call's operation name (for example, SOAP name)."""

    name: str

    __slots__ = ("name",)

    def prepare_request(self, request: Dict[str, Any]) -> None:  # noqa: D102
        request[RequiresOperationName.KEY] = self.name


operation_name = make_method_mark_decorator(OperationNameMethodMark)
