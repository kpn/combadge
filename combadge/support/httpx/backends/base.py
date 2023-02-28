from __future__ import annotations

from http import HTTPStatus
from typing import Any, Callable, Generic, Iterable, List, Tuple, Type, TypeVar
from warnings import warn

from httpx import Response
from pydantic import parse_obj_as

from combadge.core.binder import BoundResponseMarkers
from combadge.core.interfaces import ProvidesBinder
from combadge.core.typevars import ResponseT
from combadge.core.warnings import ResponseMarkNotSupported
from combadge.support.http.markers import status_code_response_mark

_ClientT = TypeVar("_ClientT")


class BaseHttpxBackend(ProvidesBinder, Generic[_ClientT]):  # noqa: D101
    _client: _ClientT
    __slots__ = ("_client",)

    def __init__(self, *, client: _ClientT) -> None:  # noqa: D107
        self._client = client

    @classmethod
    def _bind_response_markers(
        cls,
        from_: List[BoundResponseMarkers],
    ) -> List[Tuple[str, Callable[[Response], Any]]]:
        bound_marks = []
        for markers in from_:
            for marker in markers.markers:
                if marker is status_code_response_mark:
                    bound_marks.append((markers.name, lambda response: HTTPStatus(response.status_code)))
                    break
                warn(f"{marker} is not supported by {cls}", ResponseMarkNotSupported)
        return bound_marks

    @classmethod
    def _parse_response(
        cls,
        from_response: Response,
        to_type: Type[ResponseT],
        with_marks: Iterable[Tuple[str, Callable[[Response], Any]]],
    ) -> ResponseT:
        merged = {**from_response.json(), **{name: extract(from_response) for name, extract in with_marks}}
        return parse_obj_as(to_type, merged)
