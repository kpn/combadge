"""«Binding» is constructing a callable service instance from the protocol specification."""

from __future__ import annotations

from dataclasses import dataclass
from functools import update_wrapper
from inspect import BoundArguments
from inspect import getmembers as get_members
from inspect import signature as get_signature
from typing import TYPE_CHECKING, Any, Callable, Generic, Iterable, List, Mapping, Optional, Tuple, Type, TypeVar

from typing_extensions import ParamSpec

from combadge.core.markers.response import ResponseMarker

try:
    from inspect import get_annotations  # type: ignore[attr-defined]
except ImportError:
    from get_annotations import get_annotations  # type: ignore[no-redef]

from pydantic import BaseModel

from combadge.core.markers import MethodMarker, ParameterMarker
from combadge.core.response import SuccessfulResponse
from combadge.core.typevars import BackendT, Identity, ServiceProtocolT

T = TypeVar("T")
P = ParamSpec("P")

if TYPE_CHECKING:
    from combadge.core.interfaces import CallServiceMethod, MethodBinder, ProvidesBinder

    def lru_cache(maxsize: Optional[int]) -> Identity:
        ...

else:
    from functools import lru_cache


class BaseBoundService(Generic[BackendT]):
    """Parent of all bound service instances."""

    backend: BackendT
    __slots__ = ("backend",)

    def __init__(self, backend: BackendT) -> None:  # noqa: D107
        self.backend = backend


def bind(from_protocol: Type[ServiceProtocolT], to_backend: ProvidesBinder) -> ServiceProtocolT:
    """
    Create a service instance which implements the specified protocol by calling the specified backend.

    Args:
        from_protocol: service protocol description, used to extract request and response types etc.
        to_backend: backend which should perform the service requests
    """

    return bind_class(from_protocol, to_backend.binder)(to_backend)


@lru_cache(maxsize=100)
def bind_class(
    from_protocol: Type[ServiceProtocolT],
    method_binder: MethodBinder[BackendT],
) -> Callable[[BackendT], ServiceProtocolT]:
    class BoundService(BaseBoundService, from_protocol):  # type: ignore[misc, valid-type]
        """Bound service class that implements the protocol."""

    for name, method in _enumerate_methods(from_protocol):
        signature = Signature.from_method(method)
        bound_method: CallServiceMethod = method_binder(signature)
        bound_method = _wrap(bound_method, signature.method_marks)
        update_wrapper(bound_method, method)
        setattr(BoundService, name, bound_method)

    _update_bound_service(BoundService, from_protocol)
    return BoundService


def _wrap(method: Callable[P, T], with_marks: Iterable[MethodMarker]) -> Callable[P, T]:
    for mark in with_marks:
        method = mark.wrap(method)
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


def _update_bound_service(service_class: Type[BaseBoundService], with_protocol: Type[Any]) -> None:
    """Update the generated service class' magic attributes."""

    del service_class.__abstractmethods__  # type: ignore[attr-defined]
    service_class.__name__ = f"{service_class.__name__}[{with_protocol.__name__}]"
    service_class.__qualname__ = f"{service_class.__qualname__}[{with_protocol.__qualname__}]"
    service_class.__doc__ = service_class.__doc__


@dataclass
class Signature:
    """
    Contains extracted information about a service method.

    Why? Because passing all these parameters into `bind_method` would be messy.
    """

    bind_arguments: Callable[..., BoundArguments]
    method_marks: List[MethodMarker]
    parameter_marks: List[Tuple[str, ParameterMarker]]
    return_type: Type[BaseModel]
    response_marks: List[Tuple[str, List[ResponseMarker]]]

    @classmethod
    def from_method(cls, method: Any) -> Signature:
        """Create a signature from the specified method."""
        type_hints = get_annotations(method, eval_str=True)
        return_type = cls._extract_return_type(type_hints)
        return_marks = [
            (name, ResponseMarker.extract(field.annotation))
            for name, field in (getattr(return_type, "__fields__", None) or {}).items()
        ]

        return Signature(
            bind_arguments=get_signature(method).bind,
            method_marks=MethodMarker.ensure_marks(method),
            parameter_marks=list(cls._extract_parameter_marks(type_hints)),
            return_type=return_type,
            response_marks=return_marks,
        )

    @staticmethod
    def _extract_parameter_marks(from_annotations: Mapping[str, Any]) -> Iterable[Tuple[str, ParameterMarker]]:
        """Extract all parameter marks for all the parameters."""
        for name, hint in from_annotations.items():
            for mark in ParameterMarker.extract(hint):
                yield name, mark

    @staticmethod
    def _extract_return_type(from_annotations: Mapping[str, Any]) -> Type[BaseModel]:
        """Extract return type from the method."""
        return from_annotations.get("return", SuccessfulResponse)
