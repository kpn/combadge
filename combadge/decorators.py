"""Decorators to attach additional metadata to service protocol's methods."""

from typing import Callable, TypeVar

T = TypeVar("T")


def soap_name(name: str) -> Callable[[T], T]:
    """Assigns the operation name to the method."""

    def wrap(wrapped: T) -> T:
        wrapped.__soap_operation_name__ = name  # type: ignore
        return wrapped

    return wrap
