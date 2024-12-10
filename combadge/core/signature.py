from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from inspect import BoundArguments
from inspect import signature as get_signature
from typing import Any, Callable, Generic

from annotated_types import KW_ONLY, SLOTS

from combadge.core.markers import Marker
from combadge.core.service import BaseBoundService
from combadge.core.typevars import BackendRequestSpecificationT

try:
    from inspect import get_annotations  # type: ignore[attr-defined]
except ImportError:
    from get_annotations import get_annotations  # type: ignore[no-redef, import-not-found, import-untyped]


@dataclass(**SLOTS, **KW_ONLY)
class Signature:
    """Extracted information about a service method."""

    parameters_infos: Iterable[ParameterInfo]
    """All method parameters with the needed information."""

    method_markers: list[MethodMarker]
    """Extracted method markers."""

    return_type: Any | None
    """Extracted method return type."""

    bind_arguments: Callable[..., BoundArguments]
    """A callable that binds the method's arguments, it is cached here to improve performance."""

    @classmethod
    def from_method(cls, method: Any) -> Signature:
        """Create a signature from the specified method."""
        annotations_ = get_annotations(method, eval_str=True)
        return_type = cls._extract_raw_return_type(annotations_)
        return cls(
            bind_arguments=get_signature(method).bind,
            parameters_infos=cls._extract_parameter_infos(annotations_),
            method_markers=MethodMarker.ensure_markers(method),
            return_type=return_type,
        )

    def build_request(
        self,
        request_type: type[BackendRequestSpecificationT],
        service: BaseBoundService,
        call_args: Iterable[Any],
        call_kwargs: Mapping[str, Any],
    ) -> BackendRequestSpecificationT:
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
        for method_marker in self.method_markers:
            method_marker.prepare_request(request, bound_arguments)

        # Apply the parameter markers: they receive their respective values.
        all_arguments = bound_arguments.arguments
        for parameter_info in self.parameters_infos:
            try:
                value = all_arguments[parameter_info.name]
            except KeyError:
                # The parameter is not provided – skipping it.
                continue
            if callable(value):
                # Allow for lazy loaded default parameters.
                # TODO: we could potentially support async here.
                value = value()
            for parameter_marker in parameter_info.markers:
                parameter_marker(request, value)

        return request

    @staticmethod
    def _extract_parameter_infos(annotations_: dict[str, Any]) -> Iterable[ParameterInfo]:
        """Extract all the parameters with the needed associated information."""
        return tuple(
            ParameterInfo(
                name=name,
                markers=ParameterMarker.extract(annotation),
            )
            for name, annotation in annotations_.items()
        )

    @staticmethod
    def _extract_raw_return_type(annotations_: dict[str, Any]) -> type[Any] | None:
        try:
            return annotations_["return"]
        except KeyError:
            return None


@dataclass(**SLOTS)
class ParameterInfo(Generic[BackendRequestSpecificationT]):  # noqa: D101
    name: str
    """The parameter's name."""

    markers: Iterable[ParameterMarker[BackendRequestSpecificationT]]
    """The parameter's markers used to build request with the runtime parameter value."""
