from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Generic, List, Tuple, Type, TypeVar

from typing_extensions import Annotated, ParamSpec, get_origin
from typing_extensions import get_args as get_type_args

from combadge.core.typevars import RequestT

P = ParamSpec("P")
T = TypeVar("T")


class MethodMark(ABC, Generic[RequestT]):
    """Method-specific mark."""

    __slots__ = ()

    # TODO: support positional args.
    @abstractmethod
    def prepare_request(self, request: RequestT, args: Tuple[Any, ...], kwargs: Dict[str, Any]) -> None:
        """
        Modify the request according to the mark.

        Args:
            request: request that is being constructed, please refer to the ABCs for relevant keys
            args: service call positional arguments
            kwargs: service call keyword arguments
        """

    @staticmethod
    def extract(from_method: Any) -> List[MethodMark]:
        """Extract the method's marks."""
        try:
            marks = from_method.__combadge_marks__
        except AttributeError:
            marks = from_method.__combadge_marks__ = []
        return marks


def make_method_mark_decorator(type_factory: Callable[P, MethodMark]) -> Callable[P, Callable[[T], T]]:
    """Make a method decorator for the current class."""

    def decorator(*args: P.args, **kwargs: P.kwargs) -> Callable[[T], T]:
        def wrap(wrapped: T) -> T:
            MethodMark.extract(wrapped).append(type_factory(*args, **kwargs))
            return wrapped

        return wrap

    return decorator


class ParameterMark(Generic[RequestT], ABC):
    """Parameter-specific mark."""

    __slots__ = ()

    @abstractmethod
    def prepare_request(self, request: RequestT, value: Any) -> None:
        """Update the request according to the mark and the actual argument."""


def _extract_parameter_marks(type_: Type[Any]) -> List[ParameterMark]:
    if get_origin(type_) is Annotated:
        return [arg for arg in get_type_args(type_) if isinstance(arg, ParameterMark)]
    return []
