from abc import ABC
from dataclasses import InitVar, dataclass
from typing import Any, Iterable, Mapping

from combadge.core.binder import BaseBoundService
from combadge.core.signature import Signature


@dataclass
class BaseBackendRequest(ABC):  # noqa: B024
    """Base class for protocol-dependent requests."""

    signature: InitVar[Signature]
    """Extracted description of the protocol service method."""

    service: InitVar[BaseBoundService]
    """An instance of a service class, on which the method is being called."""

    call_args: InitVar[Iterable[Any]]
    """Bound method call positional arguments."""

    call_kwargs: InitVar[Mapping[str, Any]]
    """Bound method call keyword arguments."""

    def __post_init__(
        self,
        signature: Signature,
        service: BaseBoundService,
        call_args: Iterable[Any],
        call_kwargs: Mapping[str, Any],
    ) -> None:
        """Build a request using the provided request type, marks, and service call arguments."""

        bound_arguments = signature.bind_arguments(service, *call_args, **call_kwargs)
        bound_arguments.apply_defaults()

        # Apply the method markers: they receive all the arguments at once.
        for marker in signature.method_markers:
            marker.prepare_request(self, bound_arguments)

        # Apply the parameter markers: they receive their respective values.
        all_arguments = bound_arguments.arguments
        for marker in signature.parameter_descriptors:
            try:
                value = all_arguments[marker.name]
            except KeyError:
                # The parameter is not provided, skip the marker.
                pass
            else:
                # Allow for lazy loaded default parameters.
                if callable(value):
                    value = value()
                marker.prepare_request(self, value)
