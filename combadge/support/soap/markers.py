from collections.abc import Callable, Hashable
from dataclasses import dataclass
from inspect import BoundArguments
from typing import TYPE_CHECKING, Annotated, Any, Generic, TypeAlias, cast

from annotated_types import SLOTS
from typing_extensions import override

from combadge._helpers.pydantic import get_type_adapter
from combadge.core.markers.method import MethodMarker
from combadge.core.markers.parameter import ParameterMarker
from combadge.core.typevars import AnyT, FunctionT
from combadge.support.soap.abc import SoapHeader, SoapOperationName


@dataclass(**SLOTS)
class OperationName(Generic[FunctionT], MethodMarker[SoapOperationName, FunctionT]):  # noqa: D101
    name: str

    @override
    def prepare_request(self, request: SoapOperationName, _arguments: BoundArguments) -> None:  # noqa: D102
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
    return OperationName[Any](name).mark


if TYPE_CHECKING:
    Header: TypeAlias = Annotated[AnyT, ...]
else:

    @dataclass(**SLOTS)
    class Header(ParameterMarker[SoapHeader]):
        """
        Mark parameter as a request header.

        An argument gets converted to a dictionary and passed over to a backend.

        Examples:
            >>> def call(body: Annotated[HeaderModel, Header()]) -> ...:
            >>>     ...

            >>> def call(body: Header[HeaderModel]) -> ...:
            >>>     ...
        """

        exclude_unset: bool = False
        by_alias: bool = False

        @override
        def __call__(self, request: SoapHeader, value: Any) -> None:  # noqa: D102
            value = get_type_adapter(cast(Hashable, type(value))).dump_python(
                value,
                by_alias=self.by_alias,
                exclude_unset=self.exclude_unset,
            )
            if request.soap_header is None:
                request.soap_header = value
            elif isinstance(request.soap_header, dict):
                request.soap_header.update(value)  # merge into the existing header
            else:
                raise ValueError(f"attempting to merge `{type(value)}` into `{type(request.soap_header)}`")

        def __class_getitem__(cls, item: type[Any]) -> Any:
            return Annotated[item, cls()]
