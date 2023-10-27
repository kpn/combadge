from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic

from combadge.core.markers.base import AnnotatedMarker
from combadge.core.typevars import RequestT


class ParameterMarker(AnnotatedMarker, Generic[RequestT], ABC):
    """Parameter-specific marker that modifies a request with a call-time argument."""

    __slots__ = ()

    @abstractmethod
    def prepare_request(self, request: RequestT, value: Any) -> None:
        """Update the request according to the marker and the actual argument."""
