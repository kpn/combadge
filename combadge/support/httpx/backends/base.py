from __future__ import annotations

from typing import Generic, Type, TypeVar

from httpx import Response
from pydantic import parse_obj_as

from combadge.core.interfaces import ProvidesBinder
from combadge.core.typevars import ResponseT
from combadge.support.http.aliases import REASON_ALIAS, STATUS_CODE_ALIAS

_ClientT = TypeVar("_ClientT")


class BaseHttpxBackend(ProvidesBinder, Generic[_ClientT]):
    """
    [HTTPX](https://www.python-httpx.org/) client support.

    # Available response aliases

    - [`StatusCode`][combadge.support.http.aliases.StatusCode]: HTTP response status code
    - [`Reason`][combadge.support.http.aliases.Reason]: HTTP reason phrase
    """

    _client: _ClientT

    def __init__(self, client: _ClientT, *, raise_for_status: bool = True) -> None:  # noqa: D107
        self._client = client
        self._raise_for_status = raise_for_status

    @classmethod
    def _parse_response(cls, from_response: Response, to_type: Type[ResponseT]) -> ResponseT:
        return parse_obj_as(
            to_type,
            {
                STATUS_CODE_ALIAS: from_response.status_code,
                REASON_ALIAS: from_response.reason_phrase,
                **from_response.json(),
            },
        )
