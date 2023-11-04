from __future__ import annotations

from dataclasses import dataclass
from typing import Any, MutableMapping, TypeVar

from combadge.core.markers.response import ResponseMarker
from combadge.support.http.abc import SupportsStatusCode

_MutableMappingT = TypeVar("_MutableMappingT", bound=MutableMapping[Any, Any])


@dataclass
class StatusCodeMixin(ResponseMarker):
    """
    Update payload with response status code.

    Warning:
        Input payload **must be** a mutable mapping (for example, a `#!python dict`).
        If this is not the case, map it first with the [`Map` marker][combadge.core.markers.response.Map].
    """

    key: Any = "status_code"
    """Key under which the status code should assigned in the payload."""

    def transform(self, response: SupportsStatusCode, input_: _MutableMappingT) -> _MutableMappingT:  # noqa: D102
        input_[self.key] = response.status_code
        return input_
