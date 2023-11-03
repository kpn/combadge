from dataclasses import dataclass
from inspect import BoundArguments
from typing import Any, Callable, Generic

from combadge.core.markers.method import MethodMarker
from combadge.core.typevars import FunctionT
from combadge.support.soap.abc import ContainsOperationName


@dataclass
class OperationName(Generic[FunctionT], MethodMarker[ContainsOperationName, FunctionT]):  # noqa: D101
    name: str

    __slots__ = ("name",)

    def prepare_request(self, request: ContainsOperationName, _arguments: BoundArguments) -> None:  # noqa: D102
        request.operation_name = self.name


def operation_name(name: str) -> Callable[[FunctionT], FunctionT]:
    """
    Mark a service call's operation name.

    Examples:
        >>> class SupportsNumberConversion(SupportsService):
        >>>     @operation_name("NumberToWords")
        >>>     def number_to_words(self) -> ...:
        >>>         ...

    See Also:
        - [Structure of a WSDL message](https://www.ibm.com/docs/en/rtw/9.0.0?topic=documents-structure-wsdl-message)
    """
    return OperationName[Any](name)
