"""Constructs a callable service instance from the protocol specification."""

from __future__ import annotations

from dataclasses import dataclass
from functools import update_wrapper
from inspect import getmembers as get_members
from inspect import signature as get_signature
from typing import TYPE_CHECKING, Any, Callable, Generic, Iterable

from combadge.core.markers.method import MethodMarker
from combadge.core.service import BaseBoundService
from combadge.core.typevars import BackendT, FunctionT, RequestT, ServiceProtocolT

if TYPE_CHECKING:
    from combadge.core.interfaces import CallServiceMethod, MethodBinder, ProvidesBinder

    def lru_cache(maxsize: int | None) -> Callable[[FunctionT], FunctionT]:
        ...

else:
    from functools import lru_cache


def bind(from_protocol: type[ServiceProtocolT], to_backend: ProvidesBinder) -> ServiceProtocolT:
    """
    Create a service instance which implements the specified protocol by calling the specified backend.

    Args:
        from_protocol: service protocol description, used to extract request and response types etc.
        to_backend: backend which should perform the service requests
    """

    return bind_class(from_protocol, to_backend.binder)(to_backend)


@lru_cache(maxsize=100)
def bind_class(
    from_protocol: type[ServiceProtocolT],
    method_binder: MethodBinder[BackendT],
) -> Callable[[BackendT], ServiceProtocolT]:
    from combadge.core.signature import Signature

    class BoundService(BaseBoundService, from_protocol):  # type: ignore[misc, valid-type]
        """Bound service class that implements the protocol."""

        _protocol = from_protocol

    for name, method in _enumerate_methods(from_protocol):
        signature = Signature.from_method(method)
        bound_method: CallServiceMethod = method_binder(signature)
        update_wrapper(bound_method, method)
        bound_method = _wrap(bound_method, signature.method_markers)
        setattr(BoundService, name, bound_method)

    del BoundService.__abstractmethods__  # type: ignore[attr-defined]
    update_wrapper(BoundService, from_protocol, updated=())
    return BoundService


def _wrap(method: Callable[..., Any], with_markers: Iterable[MethodMarker]) -> Callable[..., Any]:
    for marker in with_markers:
        method = marker.wrap(method)
    return method


def _enumerate_methods(of_protocol: type) -> Iterable[tuple[str, Any]]:
    """Enumerate the service protocol methods."""

    for name, method in get_members(of_protocol, callable):
        if name.startswith("_"):
            continue
        parameters = get_signature(method).parameters
        if "self" not in parameters:
            continue
        yield name, method


@dataclass
class ParameterDescriptor(Generic[RequestT]):  # noqa: D101
    """
    Full description of a parameter needed to construct a request.

    Original markers are decoupled instances which can be singletons or reused.
    In order to construct a request, we need a full parameter description: its name,
    its marker, and/or its type annotation.

    This structure contains all the relevant data in a convenient form.
    """

    __slots__ = ("name", "prepare_request")

    name: str
    """Parameter name."""

    prepare_request: Callable[[RequestT, Any], None]
    """Original marker's method to prepare a request."""
