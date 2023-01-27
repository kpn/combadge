from __future__ import annotations

import inspect
from functools import update_wrapper
from typing import TYPE_CHECKING, Any, Iterable, Type, get_type_hints

from pydantic import BaseModel

from combadge.response import BaseResponse, ResponseT, SuccessfulResponse

if TYPE_CHECKING:
    from combadge.interfaces import RequestT, ServiceProtocolT, SupportsBindMethod


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

    class BoundService(BaseBoundService, from_protocol):  # type: ignore
        """Bound service class that implements the protocol."""

    for name, method in _enumerate_methods(from_protocol):
        request_type: Type[BaseModel]
        response_type: Type[BaseResponse]
        request_type, response_type = _extract_types(method)
        resolved_method = to_backend.bind_method(request_type, response_type, method)
        update_wrapper(resolved_method, method)
        setattr(BoundService, name, resolved_method)

    del BoundService.__abstractmethods__
    BoundService.__name__ = f"{BoundService.__name__}[{from_protocol.__name__}]"
    BoundService.__qualname__ = f"{BoundService.__qualname__}[{from_protocol.__qualname__}]"
    BoundService.__doc__ = from_protocol.__doc__
    return BoundService()


def _enumerate_methods(of_protocol: type) -> Iterable[tuple[str, Any]]:
    """Enumerate the service protocol methods."""

    for name, method in inspect.getmembers(of_protocol, callable):
        if name.startswith("_"):
            continue
        parameters = inspect.signature(method).parameters
        if "self" not in parameters:
            continue
        yield name, method


def _extract_types(method: Any) -> tuple[type["RequestT"], type["ResponseT"]]:
    """Extract request and response types from the method."""

    type_hints = get_type_hints(method)
    response_type = type_hints.pop("return", SuccessfulResponse)
    type_hints.pop("self", None)
    if len(type_hints) != 1:
        raise ValueError(f"expected exactly one request parameter, but got {type_hints}")
    request_type = next(iter(type_hints.values()))
    return request_type, response_type
