from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Generic, TypeVar

from combadge.core.markers.response import ResponseMarker
from combadge.support.http.abc import SupportsStatusCode

_T = TypeVar("_T")


@dataclass
class StatusCode(Generic[_T], ResponseMarker[SupportsStatusCode, Any, Dict[_T, int]]):
    """Extract status code as a dictionary from an original response."""

    key: _T
    """Key under which the status code should returned in the payload."""

    __slots__ = ("key",)

    def transform(self, response: SupportsStatusCode, input_: Any) -> Dict[_T, int]:  # noqa: D102
        return {self.key: response.status_code}
