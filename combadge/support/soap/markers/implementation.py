"""
Marker implementations.

Tip:
    It is advised to use the type aliases unless you really need to customize the behavior.
"""

from dataclasses import dataclass
from inspect import BoundArguments
from typing import Generic

from pydantic import BaseModel

from combadge.core.markers.method import MethodMarker
from combadge.core.markers.parameter import ParameterMarker
from combadge.core.typevars import FunctionT
from combadge.support.soap.abc import SupportsBody, SupportsOperationName


@dataclass
class OperationName(Generic[FunctionT], MethodMarker[SupportsOperationName, FunctionT]):
    """[`operation_name`][combadge.support.soap.markers.operation_name] marker implementation."""

    name: str

    __slots__ = ("name",)

    def prepare_request(self, request: SupportsOperationName, _arguments: BoundArguments) -> None:  # noqa: D102
        request.operation_name = self.name


@dataclass
class Body(ParameterMarker[SupportsBody]):
    """
    [Body][combadge.support.soap.markers.Body] marker implementation.

    Used for a more complex annotations, for example:

    ```python
    Annotated[BodyModel, Body(), AnotherMarker]
    ```

    For simple annotations prefer the [Body][combadge.support.soap.markers.Body] marker.
    """

    __slots__ = ()

    def prepare_request(self, request: SupportsBody, value: BaseModel) -> None:  # noqa: D102
        request.body = value.model_dump(by_alias=True)
