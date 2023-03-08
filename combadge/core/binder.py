"""«Binding» is constructing a callable service instance from the protocol specification."""

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property, update_wrapper
from inspect import BoundArguments
from inspect import getmembers as get_members
from inspect import signature as get_signature
from typing import TYPE_CHECKING, Any, Callable, Dict, Generic, Iterable, List, Optional, Type, TypeVar

from typing_extensions import ParamSpec

from combadge.core.markers.method import MethodMarker
from combadge.core.markers.parameter import ParameterMarker
from combadge.core.markers.response import ResponseMarker

try:
    from inspect import get_annotations  # type: ignore[attr-defined]
except ImportError:
    from get_annotations import get_annotations  # type: ignore[no-redef]

from pydantic import BaseModel, create_model

from combadge.core.response import SuccessfulResponse
from combadge.core.typevars import BackendT, Identity, RequestT, ServiceProtocolT

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
        bound_method = _wrap(bound_method, signature.method_markers)
        update_wrapper(bound_method, method)
        setattr(BoundService, name, bound_method)

    _update_bound_service(BoundService, from_protocol)
    return BoundService


WrappedR = TypeVar("WrappedR")
WrappedP = ParamSpec("WrappedP")


def _wrap(method: Callable[WrappedP, WrappedR], with_marks: Iterable[MethodMarker]) -> Callable[WrappedP, WrappedR]:
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


# TODO: extract into a separate module, don't forget the tests in `test_binder`.
@dataclass
class Signature:
    """
    Contains extracted information about a service method.

    Why? Because passing all these parameters into `bind_method` would be messy.
    """

    bind_arguments: Callable[..., BoundArguments]
    method_markers: List[MethodMarker]
    annotations: Dict[str, Any]

    __slots__ = ("bind_arguments", "method_markers", "annotations", "__dict__")

    @classmethod
    def from_method(cls, method: Any) -> Signature:
        """Create a signature from the specified method."""
        return Signature(
            bind_arguments=get_signature(method).bind,
            method_markers=MethodMarker.ensure_markers(method),
            annotations=get_annotations(method, eval_str=True),
        )

    @cached_property
    def parameter_descriptors(self) -> List[ParameterDescriptor]:
        """Get the parameter descriptors: separate list item for each parameter ⨯ marker combination."""
        return [
            ParameterDescriptor(name=name, prepare_request=marker.prepare_request)
            for name, annotation in self.annotations.items()
            for marker in ParameterMarker.extract(annotation)
        ]

    @cached_property
    def return_type(self) -> Type[BaseModel]:
        """Get the method's return type."""
        return self.annotations.get("return", SuccessfulResponse)

    @cached_property
    def response_descriptors(self) -> List[ResponseAttributeDescriptor]:
        """Get the response descriptors: one item for each response's attribute."""
        # FIXME: this only works for top-level attributes:
        return [
            ResponseAttributeDescriptor(name=attribute_name, markers=ResponseMarker.extract(field.annotation))
            for attribute_name, field in (getattr(self.return_type, "__fields__", None) or {}).items()
        ]

    @cached_property
    def model(self) -> Type[BaseModel]:
        """Get dynamically constructed model for this method."""
        field_definitions: Dict[str, Any] = {name: (type_, ...) for name, type_ in self.annotations.items()}
        return create_model("DynamicModel", **field_definitions)  # TODO: better model name.


ResponseMarkerT = TypeVar("ResponseMarkerT", bound=ResponseMarker)


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


@dataclass
class ResponseAttributeDescriptor(Generic[ResponseMarkerT]):  # noqa: D101
    """Describes a single response model's attribute (additional metadata needed to reconstruct a response)."""

    __slots__ = ("name", "markers")

    name: str
    """Response attribute's name."""

    markers: List[ResponseMarkerT]
    """Markers applied through `Annotated`."""
