from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Type, TypeVar

from typing_extensions import Annotated, get_origin
from typing_extensions import get_args as get_type_args

T = TypeVar("T")


class MethodMark(ABC):
    """Method-specific mark."""

    @abstractmethod
    def prepare_request(self, request: Dict[str, Any]) -> None:
        """Modify the request according to the mark."""


def _get_method_marks(method: Any) -> List[MethodMark]:
    """Extract the method's marks."""
    try:
        marks = method.__combadge_marks__
    except AttributeError:
        marks = method.__combadge_marks__ = []
    return marks


def _make_method_mark_wrapper(mark: MethodMark) -> Callable[[T], T]:
    """Make a method decorator wrapper for the specified mark."""

    def wrap(wrapped: T) -> T:
        _get_method_marks(wrapped).append(mark)
        return wrapped

    return wrap


class ParameterMark(ABC):
    """Parameter-specific mark."""

    @abstractmethod
    def prepare_request(self, request: Dict[str, Any], value: Any) -> None:
        """Update the request according to the mark and the actual argument."""


def _extract_parameter_marks(type_: Type[Any]) -> List[ParameterMark]:
    if get_origin(type_) is Annotated:
        return [arg for arg in get_type_args(type_) if isinstance(arg, ParameterMark)]
    return []
