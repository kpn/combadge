from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from inspect import BoundArguments
from inspect import signature as get_signature
from typing import Any, Callable, Iterable, Mapping, Type, cast

from pydantic import BaseModel, RootModel

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

    bind_arguments: Callable[..., BoundArguments]
    method_markers: list[MethodMarker]
    annotations: dict[str, Any]

    __slots__ = ("bind_arguments", "method_markers", "annotations", "__dict__")

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

    @classmethod
    def from_method(cls, method: Any) -> Signature:
        """Create a signature from the specified method."""
        return Signature(
            bind_arguments=get_signature(method).bind,
            method_markers=MethodMarker.ensure_markers(method),
            annotations=get_annotations(method, eval_str=True),
        )

    @cached_property
    def parameter_descriptors(self) -> list[ParameterDescriptor]:
        """Get the parameter descriptors: separate list item for each parameter ⨯ marker combination."""
        return [
            ParameterDescriptor(name=name, prepare_request=marker.prepare_request)
            for name, annotation in self.annotations.items()
            for marker in cast(Iterable[ParameterMarker], ParameterMarker.extract(annotation))
        ]

    @cached_property
    def return_type(self) -> type[BaseModel]:
        """Get the method's return type."""
        try:
            return self.annotations["return"]
        except KeyError:
            return RootModel[None]

    # TODO: `def convert_response()`.
