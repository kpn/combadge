from __future__ import annotations

from dataclasses import dataclass
from inspect import BoundArguments
from inspect import signature as get_signature
from typing import Any, Callable, Iterable, Mapping, Type, cast

from combadge.core.binder import ParameterDescriptor
from combadge.core.markers.method import MethodMarker
from combadge.core.markers.parameter import ParameterMarker
from combadge.core.service import BaseBoundService
from combadge.core.typevars import RequestT

try:
    from inspect import get_annotations  # type: ignore[attr-defined]
except ImportError:
    from get_annotations import get_annotations  # type: ignore[no-redef, import]


@dataclass
class Signature:
    """
    Contains extracted information about a service method.

    Why? Because passing all these parameters into `bind_method` would be messy.
    """

    parameter_descriptors: Iterable[ParameterDescriptor]
    """Extracted parameter descriptors, an iterable of name-marker pairs."""

    method_markers: list[MethodMarker]
    """Extracted method markers."""

    return_type: type[Any] | None
    """Extracted method return type."""

    bind_arguments: Callable[..., BoundArguments]
    """A callable that binds the method's arguments, it is cached here to improve performance."""

    __slots__ = ("bind_arguments", "method_markers", "parameter_descriptors", "return_type")

    @classmethod
    def from_method(cls, method: Any) -> Signature:
        """Create a signature from the specified method."""
        annotations_ = get_annotations(method, eval_str=True)
        return Signature(
            bind_arguments=get_signature(method).bind,
            parameter_descriptors=Signature._extract_parameter_descriptors(annotations_),
            method_markers=MethodMarker.ensure_markers(method),
            return_type=Signature._extract_return_type(annotations_),
        )

    def build_request(
        self,
        request_type: Type[RequestT],
        service: BaseBoundService,
        call_args: Iterable[Any],
        call_kwargs: Mapping[str, Any],
    ) -> RequestT:
        """
        Build a request using the provided request type, marks, and service call arguments.

        Args:
            request_type: type of the request being built
            service: an instance of a service class, on which the method is being called (`#!python self`)
            call_args: bound method call positional arguments
            call_kwargs: bound method call keyword arguments
        """

        bound_arguments = self.bind_arguments(service, *call_args, **call_kwargs)
        bound_arguments.apply_defaults()
        request = request_type()

        # Apply the method markers: they receive all the arguments at once.
        for marker in self.method_markers:
            marker.prepare_request(request, bound_arguments)

        # Apply the parameter markers: they receive their respective values.
        all_arguments = bound_arguments.arguments
        for marker in self.parameter_descriptors:
            try:
                value = all_arguments[marker.name]
            except KeyError:
                # The parameter is not provided, skip the marker.
                pass
            else:
                # Allow for lazy loaded default parameters.
                if callable(value):
                    value = value()
                marker.prepare_request(request, value)

        return request

    @staticmethod
    def _extract_parameter_descriptors(annotations_: dict[str, Any]) -> Iterable[ParameterDescriptor]:
        """Extract the parameter descriptors: separate item for each parameter ⨯ marker combination."""
        return tuple(
            ParameterDescriptor(name=name, prepare_request=marker.prepare_request)
            for name, annotation in annotations_.items()
            for marker in cast(Iterable[ParameterMarker], ParameterMarker.extract(annotation))
        )

    @staticmethod
    def _extract_return_type(annotations_: dict[str, Any]) -> type[Any] | None:
        try:
            return annotations_["return"]
        except KeyError:
            return None
