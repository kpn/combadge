from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from inspect import BoundArguments
from typing import Any, Callable, Generic

from annotated_types import SLOTS
from typing_extensions import override

from combadge.core.typevars import BackendRequestSpecificationT, FunctionT


@dataclass(**SLOTS)
class Marker(ABC, Generic[BackendRequestSpecificationT, FunctionT]):
    """Method marker that modifies an entire request based on the call arguments and/or user's metadata."""

    def mark(self, what: FunctionT) -> FunctionT:
        """
        Mark the given function with the marker.

        Notes:
            - This is not a part of the public interface and is used to derive the decorators.
            - This operates on a source unbound method stub. Any wrappers are applied during the binding stage.
        """
        Marker.ensure_markers(what).append(self)
        return what

    def wrap(self, what: FunctionT) -> FunctionT:
        """
        Wrap the function according to the marker.

        Notes:
            - Does nothing by default. Should be overridden in a child class.
            - Applied during the binding stage.
        """
        return what

    def prepare_request(self, request: BackendRequestSpecificationT, arguments: BoundArguments) -> None:
        """
        Modify the request according to the mark.

        Notes:
            - Does nothing by default. Should be overridden in a child class.

        Args:
            request: request that is being constructed, please refer to the ABCs for relevant attributes
            arguments: bound service call arguments
        """

    @staticmethod
    def ensure_markers(in_: Any) -> list[Marker]:
        """Ensure that the argument contains the mark list attribute, and return the list."""
        try:
            marks = in_.__combadge_marks__
        except AttributeError:
            marks = in_.__combadge_marks__ = []
        return marks


@dataclass(**SLOTS)
class WrapWith(Marker[Any, FunctionT], Generic[FunctionT]):  # noqa: D101
    decorator: Callable[[FunctionT], FunctionT]

    @override
    def wrap(self, what: FunctionT) -> FunctionT:  # noqa: D102
        return self.decorator(what)


def wrap_with(decorator: Callable[[Any], Any]) -> Callable[[FunctionT], FunctionT]:
    """
    Wrap the generated bound service method with decorator.

    Examples:
        >>> @wrap_with(functools.cache)
        >>> def service_method(self, ...) -> ...:
        >>>     ...

    Question: Why can I not just use a decorator directly?
        The decorator needs to wrap a method **implementation** and a service definition is just an **interface**.
        If you put it directly onto an abstract method, it would wrap only this abstract method,
        but **not** the actual implementation which is produced by [binding][binding].
    """
    return WrapWith(decorator).mark
