from __future__ import annotations

from http import HTTPStatus
from typing import Any, Callable, Generic, Iterable, List, Tuple, Type, TypeVar
from warnings import warn

from httpx import Response
from pydantic import parse_obj_as

from combadge.core.interfaces import ProvidesBinder
from combadge.core.markers.response import ResponseMarker
from combadge.core.typevars import ResponseT
from combadge.core.warnings import ResponseMarkNotSupported
from combadge.support.http.markers import status_code_response_mark

ClientT = TypeVar("ClientT")


class BaseHttpxBackend(ProvidesBinder, Generic[ClientT]):  # noqa: D101
    _client: ClientT
    __slots__ = ("_client",)

    def __init__(self, client: ClientT) -> None:  # noqa: D107
        self._client = client

    @classmethod
    def _bind_response_marks(
        cls,
        from_: List[Tuple[str, List[ResponseMarker]]],
    ) -> List[Tuple[str, Callable[[Response], Any]]]:
        bound_marks = []
        for name, marks in from_:
            for mark in marks:
                if mark is status_code_response_mark:
                    bound_marks.append((name, lambda response: HTTPStatus(response.status_code)))
                    break
                warn(f"{mark} is not supported by {cls}", ResponseMarkNotSupported)
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
