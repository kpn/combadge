from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from combadge.core.markers.base import AnnotatedMarker

_SourceT = TypeVar("_SourceT")
"""Response marker conversion source type."""

_TargetT = TypeVar("_TargetT")
"""Response marker conversion target type."""


class ResponseMarker(AnnotatedMarker, Generic[_SourceT, _TargetT], ABC):
    """Response marker: it converts a response to the target type."""

    @abstractmethod
    def transform(self, response: _SourceT) -> _TargetT:
        """Transform response from the source type to the target type."""
