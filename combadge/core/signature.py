from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from inspect import BoundArguments
from inspect import signature as get_signature
from typing import Any, Callable

from pydantic import BaseModel, RootModel

from combadge.core.binder import ParameterDescriptor
from combadge.core.markers.method import MethodMarker
from combadge.core.markers.parameter import ParameterMarker

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
            for marker in ParameterMarker.extract(annotation)
        ]

    @cached_property
    def return_type(self) -> type[BaseModel]:
        """Get the method's return type."""
        try:
            return self.annotations["return"]
        except KeyError:
            return RootModel[None]
