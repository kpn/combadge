from __future__ import annotations

import inspect
from functools import update_wrapper
from typing import TYPE_CHECKING, Any, Iterable, Type, get_type_hints

from pydantic import BaseModel

from combadge.core.response import SuccessfulResponse

if TYPE_CHECKING:
    from combadge.core.interfaces import SupportsBindMethod, SupportsServiceCall
    from combadge.core.typevars import ServiceProtocolT


class BaseBoundService:
    """Parent of all bound service instances."""


def bind(from_protocol: Type["ServiceProtocolT"], to_backend: SupportsBindMethod) -> "ServiceProtocolT":
    """
    Hereinafter «binding» is constructing a callable service instance from the protocol specification.

    This function returns an instance which implements the specified protocol
    by calling the specified backend.

    Args:
        from_protocol: service protocol description, used to extract request and response types etc.
        to_backend: backend which should perform the service requests
    """

    class BoundService(BaseBoundService, from_protocol):  # type: ignore[misc, valid-type]
        """Bound service class that implements the protocol."""

    for name, method in _enumerate_methods(from_protocol):
        response_type: Type[BaseModel] = _extract_return_type(method)
        resolved_method: SupportsServiceCall = to_backend.bind_method(response_type, method)
        update_wrapper(resolved_method, method)
        setattr(BoundService, name, resolved_method)

    _update_bound_service(BoundService, from_protocol)
    return BoundService()


def _update_bound_service(service_class: Type[BaseBoundService], with_protocol: Type[Any]) -> None:
    """Update the generated service class' magic attributes."""

    del service_class.__abstractmethods__  # type: ignore
    service_class.__name__ = f"{service_class.__name__}[{with_protocol.__name__}]"
    service_class.__qualname__ = f"{service_class.__qualname__}[{with_protocol.__qualname__}]"
    service_class.__doc__ = service_class.__doc__


def _enumerate_methods(of_protocol: type) -> Iterable[tuple[str, Any]]:
    """Enumerate the service protocol methods."""

    for name, method in inspect.getmembers(of_protocol, callable):
        if name.startswith("_"):
            continue
        parameters = inspect.signature(method).parameters
        if "self" not in parameters:
            continue
        yield name, method


def _extract_return_type(method: Any) -> Type[BaseModel]:
    """Extract return type from the method."""
    return get_type_hints(method).pop("return", SuccessfulResponse)
