from __future__ import annotations

from http import HTTPStatus
from typing import Any, Callable, Generic, Iterable, List, Tuple, Type, TypeVar
from warnings import warn

from httpx import Response
from pydantic import parse_obj_as

from combadge.core.binder import ResponseAttributeDescriptor
from combadge.core.interfaces import ProvidesBinder
from combadge.core.typevars import ResponseT
from combadge.core.warnings import ResponseMarkerNotSupported
from combadge.support.http.markers import status_code_response_mark

_ClientT = TypeVar("_ClientT")


class BaseHttpxBackend(ProvidesBinder, Generic[_ClientT]):  # noqa: D101
    _client: _ClientT
    __slots__ = ("_client",)

    def __init__(self, *, client: _ClientT) -> None:  # noqa: D107
        self._client = client

    @classmethod
    def _build_response_extractors(
        cls,
        from_descriptors: List[ResponseAttributeDescriptor],
    ) -> List[Tuple[str, Callable[[Response], Any]]]:
        bound_marks = []
        for descriptor in from_descriptors:
            for marker in descriptor.markers:
                if marker is status_code_response_mark:
                    bound_marks.append((descriptor.name, lambda response: HTTPStatus(response.status_code)))
                    break
                warn(f"{marker} is not supported by {cls}", ResponseMarkerNotSupported)
        return bound_marks

    @classmethod
    def _parse_response(
        cls,
        from_response: Response,
        to_type: Type[ResponseT],
        with_extractors: Iterable[Tuple[str, Callable[[Response], Any]]],
    ) -> ResponseT:
        merged = {**from_response.json(), **{name: extract(from_response) for name, extract in with_extractors}}
        return parse_obj_as(to_type, merged)
