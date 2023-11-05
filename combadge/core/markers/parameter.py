from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic

from combadge.core.markers.base import AnnotatedMarker
from combadge.core.typevars import BackendRequestT


class ParameterMarker(AnnotatedMarker, Generic[BackendRequestT], ABC):
    """Parameter marker: it modifies a request with a call-time argument."""

    __slots__ = ()

    @abstractmethod
    def __call__(self, request: BackendRequestT, value: Any) -> None:
        """Update the request according to the marker and the actual argument."""
