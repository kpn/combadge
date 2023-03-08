from __future__ import annotations

from typing import Generic, Type, TypeVar

from httpx import Response
from pydantic import parse_obj_as

from combadge.core.interfaces import ProvidesBinder
from combadge.core.typevars import ResponseT

_ClientT = TypeVar("_ClientT")


class BaseHttpxBackend(ProvidesBinder, Generic[_ClientT]):
    """
    [HTTPX](https://www.python-httpx.org/) client support.

    # Available response aliases

    - `__reason__`: HTTP reason phrase
    - `__status_code__`: HTTP response status code
    """

    _client: _ClientT
    __slots__ = ("_client",)

    def __init__(self, *, client: _ClientT) -> None:  # noqa: D107
        self._client = client

    @classmethod
    def _parse_response(cls, from_response: Response, to_type: Type[ResponseT]) -> ResponseT:
        return parse_obj_as(
            to_type,
            {
                "__status_code__": from_response.status_code,
                "__reason__": from_response.reason_phrase,
                **from_response.json(),
            },
        )
