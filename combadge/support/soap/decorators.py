from typing import Callable, TypeVar

from combadge.core.mark import _make_method_mark_wrapper
from combadge.support.soap.marks import OperationNameMark

T = TypeVar("T")


def operation_name(name: str) -> Callable[[T], T]:
    """Assign the SOAP operation name to the method."""
    return _make_method_mark_wrapper(OperationNameMark(name))
