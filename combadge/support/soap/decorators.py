from typing import Callable, TypeVar

T = TypeVar("T")


def soap_name(name: str) -> Callable[[T], T]:
    """Assign the SOAP operation name to the method."""

    def wrap(wrapped: T) -> T:
        wrapped.__soap_operation_name__ = name  # type: ignore[attr-defined]
        return wrapped

    return wrap
