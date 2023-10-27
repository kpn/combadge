"""
Marker implementations.

Tip:
    It is advised to use the type aliases unless you really need to customize the behavior.
"""

from dataclasses import dataclass
from inspect import BoundArguments
from typing import Any, Generic

from combadge.core.markers.method import MethodMarker
from combadge.core.markers.parameter import ParameterMarker
from combadge.core.typevars import FunctionT
from combadge.support.soap.abc import RequiresBody, RequiresOperationName


@dataclass
class OperationName(Generic[FunctionT], MethodMarker[RequiresOperationName, FunctionT]):
    """[`operation_name`][combadge.support.soap.markers.operation_name] marker implementation."""

    name: str

    __slots__ = ("name",)

    def prepare_request(self, request: RequiresOperationName, _arguments: BoundArguments) -> None:  # noqa: D102
        request.operation_name = self.name


@dataclass
class Body(ParameterMarker[RequiresBody]):
    """
    [Body][combadge.support.soap.markers.Body] marker implementation.

    Used for a more complex annotations, for example:

    ```python
    Annotated[BodyModel, Body(), AnotherMarker]
    ```

    For simple annotations prefer the [Body][combadge.support.soap.markers.Body] marker.
    """

    __slots__ = ()

    def prepare_request(self, request: RequiresBody, value: Any) -> None:  # noqa: D102
        request.body = value
