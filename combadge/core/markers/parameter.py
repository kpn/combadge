from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic

from typing_extensions import Annotated, get_origin
from typing_extensions import get_args as get_type_args

from combadge.core.typevars import RequestT


class ParameterMarker(Generic[RequestT], ABC):
    """Parameter-specific marker that modifies a request with a call-time argument."""

    __slots__ = ()

    @staticmethod
    def extract(type_: type[Any]) -> list[ParameterMarker]:
        """Extract all parameter markers from the type annotation."""
        if get_origin(type_) is Annotated:
            return [arg for arg in get_type_args(type_) if isinstance(arg, ParameterMarker)]
        return []

    @abstractmethod
    def prepare_request(self, request: RequestT, value: Any) -> None:
        """Update the request according to the marker and the actual argument."""
