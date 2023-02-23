from __future__ import annotations

from abc import ABC
from typing import Any, Dict, Generic, List, Tuple, TypeVar

from combadge.core.typevars import Identity, RequestT

T = TypeVar("T")


class MethodMarker(ABC, Generic[RequestT]):
    """Method-specific marker that modifies an entire request based on all the call arguments."""

    __slots__ = ()

    def wrap(self, what: T) -> T:
        """
        Wrap the argument according to the marker.

        Notes:
            - Does nothing by default. Override in a child class.
        """
        return what

    def prepare_request(self, request: RequestT, args: Tuple[Any, ...], kwargs: Dict[str, Any]) -> None:
        """
        Modify the request according to the mark.

        Notes:
            - Does nothing by default. Override in a child class.

        Args:
            request: request that is being constructed, please refer to the ABCs for relevant keys
            args: service call positional arguments
            kwargs: service call keyword arguments
        """

    @staticmethod
    def ensure_marks(in_: Any) -> List[MethodMarker]:
        """Ensure that the argument contains the mark list attribute, and return the list."""
        try:
            marks = in_.__combadge_marks__
        except AttributeError:
            marks = in_.__combadge_marks__ = []
        return marks

    def mark(self, what: T) -> T:
        """
        Mark the argument with itself.

        This is not a part of the public interface and is used to derive the decorators.
        """
        MethodMarker.ensure_marks(what).append(self)
        return what


class _DecorateMethodMarker(MethodMarker[Any]):
    _decorator: Identity
    __slots__ = ("_decorator",)

    def __init__(self, decorator: Identity) -> None:
        self._decorator = decorator

    def wrap(self, what: T) -> T:
        return self._decorator(what)


def decorator(decorator: Identity[T]) -> Identity[T]:
    """
    Put the decorator on top of the generated bound service method.

    Example:
        >>> @decorator(functools.cache())
        >>> def service_method(self, ...) -> ...:
        >>>     ...
    """
    return _DecorateMethodMarker(decorator).mark
