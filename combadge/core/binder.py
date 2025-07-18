"""Constructs a callable service instance from the protocol specification."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from functools import update_wrapper
from inspect import getmembers as get_members
from inspect import signature as get_signature
from typing import TYPE_CHECKING, Any

from typing_extensions import override

from combadge.core.markers.method import MethodMarker
from combadge.core.service import BaseBoundService
from combadge.core.typevars import BackendT, FunctionT, ServiceProtocolT

if TYPE_CHECKING:
    from combadge.core.backend import BaseBackend
    from combadge.core.interfaces import ServiceMethod

    def lru_cache(maxsize: int | None) -> Callable[[FunctionT], FunctionT]: ...

else:
    from functools import lru_cache


def bind(from_protocol: type[ServiceProtocolT], to_backend: BaseBackend) -> ServiceProtocolT:
    """
    Create a service instance which implements the specified protocol by calling the specified backend.

    Args:
        from_protocol: service protocol description, used to extract request and response types etc.
        to_backend: backend which should perform the service requests
    """

    return bind_class(from_protocol, to_backend)(to_backend)


@lru_cache(maxsize=100)
def bind_class(
    from_protocol: type[ServiceProtocolT],
    to_backend: BackendT,
) -> Callable[[BackendT], ServiceProtocolT]:
    """Create a class which implements the specified protocol, but not yet parametrized with a backend."""

    from combadge.core.signature import Signature

    class BoundService(BaseBoundService, from_protocol):  # type: ignore[misc, valid-type]
        """Bound service class that implements the protocol."""

        __combadge_protocol__ = from_protocol

    for name, method in _enumerate_methods(from_protocol):
        signature = Signature.from_method(method)
        bound_method: ServiceMethod = to_backend.bind_method(signature)  # generate implementation by the backend
        update_wrapper(bound_method, method)
        bound_method = _wrap(bound_method, signature.method_markers)
        bound_method = override(bound_method)  # no functional change, just possibly setting `__override__`
        setattr(BoundService, name, bound_method)

    del BoundService.__abstractmethods__
    update_wrapper(BoundService, from_protocol, updated=())
    return BoundService


def _wrap(method: FunctionT, with_markers: Iterable[MethodMarker]) -> FunctionT:
    """
    Apply method markers.

    Method markers may wrap or modify the bound method.

    Args:
        method: bound method in the protocol implementation
        with_markers: method markers to apply
    """
    for marker in with_markers:
        method = marker.wrap(method)
    return method


def _enumerate_methods(of_protocol: type) -> Iterable[tuple[str, Callable[..., Any]]]:
    """Enumerate the service protocol methods."""

    for name, method in get_members(of_protocol, callable):
        if name.startswith("_") and name != "__call__":
            continue
        parameters = get_signature(method).parameters
        if "self" not in parameters:
            continue
        yield name, method
