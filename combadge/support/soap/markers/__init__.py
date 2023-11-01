"""
Marker implementations.

Tip:
    It is advised to use the type aliases unless you really need to customize the behavior.
"""

from dataclasses import dataclass
from inspect import BoundArguments
from typing import Generic

from combadge.core.markers.method import MethodMarker
from combadge.core.typevars import FunctionT
from combadge.support.soap.abc import ContainsOperationName


@dataclass
class OperationName(Generic[FunctionT], MethodMarker[ContainsOperationName, FunctionT]):
    """[`operation_name`][combadge.support.soap.markers.shortcuts.operation_name] marker implementation."""

    name: str

    __slots__ = ("name",)

    def prepare_request(self, request: ContainsOperationName, _arguments: BoundArguments) -> None:  # noqa: D102
        request.operation_name = self.name
