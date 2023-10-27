from typing import Any, Callable, TypeVar

from typing_extensions import Annotated, TypeAlias

from combadge.core.typevars import FunctionT

from .implementation import Body as BodyImplementation
from .implementation import OperationName


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
    return OperationName[Any](name).mark


_T = TypeVar("_T")


Body: TypeAlias = Annotated[_T, BodyImplementation()]
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
