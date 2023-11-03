from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from combadge.core.markers.base import AnnotatedMarker

_InputT = TypeVar("_InputT")
"""Response marker conversion input type."""

OutputT = TypeVar("OutputT")
"""Response marker conversion output type."""


class ResponseMarker(AnnotatedMarker, Generic[_InputT, OutputT], ABC):
    """Response marker: it converts a response to the target type."""

    @abstractmethod
    def transform(self, input_: _InputT) -> OutputT:
        """Transform response from the source type to the target type."""
