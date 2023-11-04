from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, TypeVar

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
    """
    Map a payload to a dictionary under the specified key.

    Other Args:
        _InputPayloadT (type): input payload type
    """

    key: Any
    """Key under which the response will be mapped."""

    def transform(self, response: Any, payload: Any) -> Dict[Any, Any]:  # noqa: D102
        return {self.key: payload}
