from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Mapping, MutableMapping, TypeVar

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

    def __call__(self, response: Any, payload: Mapping[Any, Any]) -> Any:  # noqa: D102
        return payload[self.key]


_MutableMappingT = TypeVar("_MutableMappingT", bound=MutableMapping[Any, Any])


@dataclass
class Mixin(ResponseMarker):
    """Mix in the inner marker output to the payload."""

    inner: ResponseMarker
    """Inner marker to apply to a payload."""

    __slots__ = ("inner",)

    def __call__(self, response: Any, payload: _MutableMappingT) -> _MutableMappingT:  # noqa: D102
        payload.update(self.inner(response, payload))
        return payload
