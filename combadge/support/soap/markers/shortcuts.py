from typing import Any, Callable

from combadge.core.typevars import FunctionT

from . import OperationName


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
