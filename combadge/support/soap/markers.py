from dataclasses import dataclass
from typing import Any, Dict, Tuple

from combadge.core.markers import MethodMarker
from combadge.core.typevars import Identity
from combadge.support.soap.abc import RequiresOperationName


@dataclass
class _OperationNameMethodMarker(MethodMarker[RequiresOperationName]):
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
    return _OperationNameMethodMarker(name).mark
