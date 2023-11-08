from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Mapping, MutableMapping, TypeVar

# noinspection PyUnresolvedReferences
from typing_extensions import override

from combadge.core.markers.base import AnnotatedMarker

_InputPayloadT = TypeVar("_InputPayloadT")
_OutputPayloadT = TypeVar("_OutputPayloadT")


class ResponseMarker(AnnotatedMarker, ABC):
    """Response marker: it transforms or contructs a response."""

    __slots__ = ()

    @abstractmethod
    def __call__(self, response: Any, payload: Any) -> Any:
        """Transform the response."""


@dataclass
class Map(ResponseMarker):
    """Map a payload to a dictionary under the specified key."""

    key: Any
    """Key under which the response will be mapped."""

    __slots__ = ("key",)

    @override
    def __call__(self, response: Any, payload: Any) -> Dict[Any, Any]:  # noqa: D102
        return {self.key: payload}


@dataclass
class Extract(ResponseMarker):
    """
    Extract a value from the specified key.

    Examples:
        >>> def call() -> Annotated[
        >>>     HTTPStatus,
        >>>     StatusCode(),            # Drop the original payload and return the status code
        >>>     Extract("status_code"),  # Extract the status code
        >>> ]:
        >>>     ...
    """

    key: Any
    """Key which will be extracted from the payload."""

    __slots__ = ("key",)

    @override
    def __call__(self, response: Any, payload: Mapping[Any, Any]) -> Any:  # noqa: D102
        return payload[self.key]


_MutableMappingT = TypeVar("_MutableMappingT", bound=MutableMapping[Any, Any])


@dataclass(init=False)
class Mixin(ResponseMarker):
    """Mix in the inner marker outputs to the payload."""

    inner: Iterable[ResponseMarker]

    __slots__ = ("inner",)

    def __init__(self, *inner: ResponseMarker) -> None:
        """
        Initialize the marker.

        Args:
            *inner: inner markers to apply to a payload
        """
        self.inner = inner

    @override
    def __call__(self, response: Any, payload: _MutableMappingT) -> _MutableMappingT:  # noqa: D102
        for marker in self.inner:
            payload.update(marker(response, payload))
        return payload
