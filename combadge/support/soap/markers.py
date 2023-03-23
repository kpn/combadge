from dataclasses import dataclass
from inspect import BoundArguments
from typing import Any, Callable, Generic, TypeVar

from typing_extensions import Annotated, TypeAlias

from combadge.core.markers.method import MethodMarker
from combadge.core.markers.parameter import ParameterMarker
from combadge.core.typevars import FunctionT
from combadge.support.soap.abc import RequiresBody, RequiresOperationName


@dataclass
class _OperationNameMarker(Generic[FunctionT], MethodMarker[RequiresOperationName, FunctionT]):
    name: str

    __slots__ = ("name",)

    def prepare_request(self, request: RequiresOperationName, _arguments: BoundArguments) -> None:  # noqa: D102
        request.operation_name = self.name


def operation_name(name: str) -> Callable[[FunctionT], FunctionT]:
    """
    Mark a service call's operation name.

    Examples:
        >>> from combadge.support.soap.markers import operation_name
        >>>
        >>> class SupportsNumberConversion(SupportsService):
        >>>     @operation_name("NumberToWords")
        >>>     def number_to_words(self) -> ...:
        >>>         ...

    See Also:
        - [Structure of a WSDL message](https://www.ibm.com/docs/en/rtw/9.0.0?topic=documents-structure-wsdl-message)
    """
    return _OperationNameMarker[Any](name).mark


_T = TypeVar("_T")


@dataclass
class BodyMarker(ParameterMarker[RequiresBody]):
    """
    Marker class for the [Body][combadge.support.soap.markers.Body] marker.

    Used for a more complex annotations, for example:

    ```python
    Annotated[BodyModel, BodyParameterMarker(), AnotherMarker]
    ```

    For simple annotations prefer the [Body][combadge.support.soap.markers.Body] marker.
    """

    __slots__ = ()

    def prepare_request(self, request: RequiresBody, value: Any) -> None:  # noqa: D102
        request.body = value


Body: TypeAlias = Annotated[_T, BodyMarker()]
"""
Mark parameter as a request body. An argument gets converted to a dictionary and passed over to a backend.

Examples:
    >>> from combadge.support.http import Body
    >>>
    >>> class BodyModel(BaseModel):
    >>>     ...
    >>>
    >>> def call(body: Body[BodyModel]) -> ...:
    >>>     ...
"""
