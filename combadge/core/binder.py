from __future__ import annotations

from dataclasses import dataclass
from functools import update_wrapper
from inspect import Signature as BuiltinSignature
from inspect import getmembers as get_members
from inspect import signature as get_signature
from typing import TYPE_CHECKING, Any, Iterable, List, Mapping, Tuple, Type

try:
    from inspect import get_annotations
except ImportError:
    from get_annotations import get_annotations  # type: ignore[no-redef]

from pydantic import BaseModel

from combadge.core.mark import MethodMark, ParameterMark, _extract_parameter_marks, _get_method_marks
from combadge.core.response import SuccessfulResponse

if TYPE_CHECKING:
    from combadge.core.interfaces import SupportsBindServiceMethod, SupportsServiceMethodCall
    from combadge.core.typevars import ServiceProtocolT


class BaseBoundService:
    """Parent of all bound service instances."""


def bind(from_protocol: Type["ServiceProtocolT"], to_backend: SupportsBindServiceMethod) -> "ServiceProtocolT":
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
        signature = Signature.from_method(method)
        resolved_method: SupportsServiceMethodCall = to_backend.bind_method(signature)
        update_wrapper(resolved_method, method)
        setattr(BoundService, name, resolved_method)

    _update_bound_service(BoundService, from_protocol)
    return BoundService()


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

    del service_class.__abstractmethods__  # type: ignore
    service_class.__name__ = f"{service_class.__name__}[{with_protocol.__name__}]"
    service_class.__qualname__ = f"{service_class.__qualname__}[{with_protocol.__qualname__}]"
    service_class.__doc__ = service_class.__doc__


@dataclass
class Signature:
    """
    Contains extracted information about a service method.

    Why? Because passing all these parameters into `bind_method` would be messy.
    """

    inner: BuiltinSignature
    method_marks: List[MethodMark]
    parameter_marks: List[Tuple[str, ParameterMark]]
    return_type: Type[BaseModel]

    @classmethod
    def from_method(cls, method: Any) -> Signature:
        """Create a signature from the specified method."""
        type_hints = get_annotations(method, eval_str=True)
        return Signature(
            inner=get_signature(method),
            method_marks=_get_method_marks(method),
            parameter_marks=list(cls._extract_parameter_marks(type_hints)),
            return_type=cls._extract_return_type(type_hints),
        )

    @staticmethod
    def _extract_parameter_marks(annotations: Mapping[str, Any]) -> Iterable[Tuple[str, ParameterMark]]:
        """Extract all parameter marks for all the parameters."""
        for name, hint in annotations.items():
            for mark in _extract_parameter_marks(hint):
                yield name, mark

    @staticmethod
    def _extract_return_type(annotations: Mapping[str, Any]) -> Type[BaseModel]:
        """Extract return type from the method."""
        return annotations.get("return", SuccessfulResponse)
