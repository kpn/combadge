from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Mapping, TypeVar

from combadge.core.markers.base import AnnotatedMarker

_InputPayloadT = TypeVar("_InputPayloadT")
_OutputPayloadT = TypeVar("_OutputPayloadT")


class ResponseMarker(AnnotatedMarker, ABC):
    """Response marker: it converts a response to the target type."""

    @abstractmethod
    def transform(self, response: Any, payload: Any) -> Any:
        """Transform response from the source type to the target type."""


@dataclass
class Map(ResponseMarker):
    """Map a payload to a dictionary under the specified key."""

    key: Any
    """Key under which the response will be mapped."""

    def transform(self, response: Any, payload: Any) -> Dict[Any, Any]:  # noqa: D102
        return {self.key: payload}


@dataclass
class GetItem(ResponseMarker):
    """
    Extract a value from the specified key.

    Examples:
        >>> def call() -> Annotated[
        >>>     int,                     # Status code is an integer
        >>>     Drop(),                  # Drop the payload
        >>>     StatusCodeMixin(),       # Mix in the status code from the HTTP response
        >>>     GetItem("status_code"),  # Extract the status code
        >>> ]:
        >>>     ...
    """

    key: Any
    """Key which will be extracted from the payload."""

    def transform(self, response: Any, payload: Mapping[Any, Any]) -> Any:  # noqa: D102
        return payload[self.key]


class Drop(ResponseMarker):  # pragma: no cover
    """
    Drop the payload.

    It might be useful if one is only interested, for example, in an HTTP status code:

    Examples:
        >>> def call() -> Annotated[..., Drop(), StatusCodeMixin()]
        >>>     ...
    """

    __slots__ = ()

    def transform(self, response: Any, payload: Any) -> Dict[Any, Any]:  # noqa: D102
        return {}
