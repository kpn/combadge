from __future__ import annotations

from abc import ABC
from inspect import BoundArguments
from typing import Any, Callable, Generic

from combadge.core.typevars import FunctionT, RequestT


class MethodMarker(ABC, Generic[RequestT, FunctionT]):
    """Method-specific marker that modifies an entire request based on all the call arguments."""

    __slots__ = ()

    def wrap(self, what: FunctionT) -> FunctionT:
        """
        Wrap the argument according to the marker.

        Notes:
            - Does nothing by default. Override in a child class.
        """
        return what

    def prepare_request(self, request: RequestT, arguments: BoundArguments) -> None:
        """
        Modify the request according to the mark.

        Notes:
            - Does nothing by default. Override in a child class.

        Args:
            request: request that is being constructed, please refer to the ABCs for relevant keys
            arguments: bound service call arguments
        """

    @staticmethod
    def ensure_markers(in_: Any) -> list[MethodMarker]:
        """Ensure that the argument contains the mark list attribute, and return the list."""
        try:
            marks = in_.__combadge_marks__
        except AttributeError:
            marks = in_.__combadge_marks__ = []
        return marks

    def mark(self, what: FunctionT) -> FunctionT:
        """
        Mark the argument with itself.

        This is not a part of the public interface and is used to derive the decorators.
        """
        MethodMarker.ensure_markers(what).append(self)
        return what


class _WrapWithMethodMarker(Generic[FunctionT], MethodMarker[Any, FunctionT]):
    __slots__ = ("_decorator",)

    def __init__(self, decorator: Callable[[FunctionT], FunctionT]) -> None:
        self._decorator = decorator

    def wrap(self, what: FunctionT) -> FunctionT:
        return self._decorator(what)


def wrap_with(decorator: Callable[[Any], Any]) -> Callable[[FunctionT], FunctionT]:
    """
    Put the decorator on top of the generated bound service method.

    Examples:
        >>> @wrap_with(functools.cache)
        >>> def service_method(self, ...) -> ...:
        >>>     ...

    Note: Decorator cannot change function signature
        At the moment the type hinting is limited to decorators, which do not change
        a wrapped function's signature – possible Mypy's limitation.

        It will still work at runtime, but Mypy will very likely complain if you do so.
    """
    return _WrapWithMethodMarker(decorator).mark
