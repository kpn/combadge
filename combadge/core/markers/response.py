from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, Iterable, Mapping, MutableMapping, TypeVar

from combadge.core.markers.base import AnnotatedMarker
from combadge.core.typevars import BackendResponseT

_InputPayloadT = TypeVar("_InputPayloadT")
_OutputPayloadT = TypeVar("_OutputPayloadT")


class ResponseMarker(AnnotatedMarker, Generic[BackendResponseT, _InputPayloadT, _OutputPayloadT], ABC):
    """Response marker: it converts a response to the target type."""

    @abstractmethod
    def transform(self, response: BackendResponseT, payload: _InputPayloadT) -> _OutputPayloadT:
        """Transform response from the source type to the target type."""


_MutableMappingT = TypeVar("_MutableMappingT", bound=MutableMapping[Any, Any])


class Mixin(ResponseMarker[Any, _MutableMappingT, _MutableMappingT]):
    """
    Mix the inner marker outputs into the payload.

    Warning:
        - The payload **must** be a mutable mapping (for example, `#!python dict`)
        - The inner markers **must** return their outputs as a mapping
    """

    _inner: Iterable[ResponseMarker[Any, Mapping[Any, Any], Mapping[Any, Any]]]

    __slots__ = ("_inner",)

    def __init__(self, *inner: ResponseMarker[Any, Mapping[Any, Any], Mapping[Any, Any]]) -> None:
        """
        Initialize the marker.

        Args:
            *inner: inner markers
        """
        self._inner = inner

    def transform(self, response: Any, payload: _MutableMappingT) -> _MutableMappingT:  # noqa: D102
        for marker in self._inner:
            payload.update(marker.transform(response, payload))
        return payload
