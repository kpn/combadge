from __future__ import annotations

from dataclasses import dataclass
from http import HTTPStatus
from typing import Any, Generic, TypeVar

from annotated_types import KW_ONLY, SLOTS
from httpx import AsyncClient, Client, Response
from pydantic import TypeAdapter

from combadge._helpers.pydantic import get_type_adapter
from combadge.core.interfaces import SupportsBackend
from combadge.core.signature import Signature
from combadge.support.http.request import Request
from combadge.support.httpx.response import ResponseDict

_ClientT = TypeVar("_ClientT", Client, AsyncClient)


@dataclass(**SLOTS, **KW_ONLY)
class MethodMeta:  # noqa: D101
    response_adapter: TypeAdapter[Any]
    """Wrapped original return type which was extracted from the method signature."""


class BaseHttpxBackend(SupportsBackend[Request, MethodMeta], Generic[_ClientT]):
    """[HTTPX](https://www.python-httpx.org/) client support."""

    REQUEST_TYPE = Request

    _client: _ClientT

    def __init__(self, client: _ClientT, *, raise_for_status: bool = True) -> None:  # noqa: D107
        self._client = client
        self._raise_for_status = raise_for_status

    @classmethod
    def inspect(cls, signature: Signature) -> MethodMeta:  # noqa: D102
        return MethodMeta(response_adapter=get_type_adapter(signature.return_type))

    def _parse_response(self, meta: MethodMeta, response: Response) -> Any:
        """Parse the given native response from HTTPX."""
        if self._raise_for_status:
            response.raise_for_status()
        if meta.response_adapter is None:
            # Fast return, if the response is ignored by the service protocol.
            return None
        try:
            # TODO: need to support additional serialization formats.
            body = response.json()
        except ValueError:
            body = response.text
        response_dict: ResponseDict = {
            "body": body,
            "http": {
                "status": HTTPStatus(response.status_code),
                "reason": response.reason_phrase,
                "headers": response.headers,
            },
        }
        return meta.response_adapter.validate_python(response_dict)
