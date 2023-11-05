from __future__ import annotations

from dataclasses import dataclass
from inspect import BoundArguments
from inspect import signature as get_signature
from typing import Any, Callable, Generic, Iterable, Mapping, Type

from pydantic import BaseModel, TypeAdapter

from combadge.core.markers.method import MethodMarker
from combadge.core.markers.parameter import ParameterMarker
from combadge.core.markers.response import ResponseMarker
from combadge.core.service import BaseBoundService
from combadge.core.typevars import BackendRequestT, ResponseT

try:
    from inspect import get_annotations  # type: ignore[attr-defined]
except ImportError:
    from get_annotations import get_annotations  # type: ignore[no-redef, import-not-found, import-untyped]


@dataclass
class Signature:
    """Extracted information about a service method."""

    request_preparers: Iterable[RequestPreparer]
    """Request preparers constructed from the parameter markers."""

    method_markers: list[MethodMarker]
    """Extracted method markers."""

    return_type: type[Any] | None
    """Extracted method return type."""

    response_markers: Iterable[ResponseMarker]
    """Response markers extracted from the return type"""

    bind_arguments: Callable[..., BoundArguments]
    """A callable that binds the method's arguments, it is cached here to improve performance."""

    __slots__ = ("bind_arguments", "method_markers", "request_preparers", "return_type", "response_markers")

    @classmethod
    def from_method(cls, method: Any) -> Signature:
        """Create a signature from the specified method."""
        annotations_ = get_annotations(method, eval_str=True)
        return_type = Signature._extract_return_type(annotations_)
        return Signature(
            bind_arguments=get_signature(method).bind,
            request_preparers=Signature._build_request_preparers(annotations_),
            method_markers=MethodMarker.ensure_markers(method),
            return_type=return_type,
            response_markers=ResponseMarker.extract(return_type),
        )

    def build_request(
        self,
        request_type: Type[BackendRequestT],
        service: BaseBoundService,
        call_args: Iterable[Any],
        call_kwargs: Mapping[str, Any],
    ) -> BackendRequestT:
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
        for preparer in self.request_preparers:
            try:
                value = all_arguments[preparer.parameter_name]
            except KeyError:
                # The parameter is not provided, skip the marker.
                continue
            if callable(value):
                # Allow for lazy loaded default parameters.
                value = value()
            for prepare_request in preparer.prepare_request:
                prepare_request(request, value)

        return request

    def apply_response_markers(self, response: Any, payload: Any, response_type: TypeAdapter[ResponseT]) -> ResponseT:
        """
        Apply the response markers to the payload sequentially.

        Args:
            response: original backend response
            payload: parsed response payload
            response_type: user response type (we require type adapter because the inner type may be anything)
        """
        for marker in self.response_markers:
            payload = marker(response, payload)
        if not isinstance(payload, BaseModel):
            # Implicitly parse a Pydantic model.
            # Need to come up with something smarter to uncouple Combadge from Pydantic.
            payload = response_type.validate_python(payload)
        return payload

    @staticmethod
    def _build_request_preparers(annotations_: dict[str, Any]) -> Iterable[RequestPreparer]:
        """Extract the parameter descriptors: separate item for each parameter ⨯ marker combination."""
        return tuple(
            RequestPreparer(
                parameter_name=name,
                prepare_request=ParameterMarker.extract(annotation),
            )
            for name, annotation in annotations_.items()
        )

    @staticmethod
    def _extract_return_type(annotations_: dict[str, Any]) -> type[Any] | None:
        try:
            return annotations_["return"]
        except KeyError:
            return None


@dataclass
class RequestPreparer(Generic[BackendRequestT]):  # noqa: D101
    __slots__ = ("parameter_name", "prepare_request")

    parameter_name: str

    prepare_request: Iterable[Callable[[BackendRequestT, Any], None]]
    """Collection of callables, which modify the request based on the parameter's value."""
