from __future__ import annotations

from collections.abc import Hashable
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from annotated_types import KW_ONLY, SLOTS
from httpx import AsyncClient, Client, Response
from pydantic import TypeAdapter

from combadge._helpers.pydantic import get_type_adapter
from combadge.core.interfaces import ProvidesBinder, SupportsBackend
from combadge.core.signature import Signature
from combadge.support.http.request import Request

_ClientT = TypeVar("_ClientT", Client, AsyncClient)


@dataclass(**SLOTS, **KW_ONLY)
class MethodMeta:  # noqa: D101
    response_type: TypeAdapter[Any]
    """Response type extracted from the original signature."""


class BaseHttpxBackend(ProvidesBinder, SupportsBackend[Request, MethodMeta], Generic[_ClientT]):
    """[HTTPX](https://www.python-httpx.org/) client support."""

    REQUEST_TYPE = Request

    _client: _ClientT

    def __init__(self, client: _ClientT, *, raise_for_status: bool = True) -> None:  # noqa: D107
        self._client = client
        self._raise_for_status = raise_for_status

    @classmethod
    def inspect(cls, signature: Signature) -> MethodMeta:  # noqa: D102
        assert isinstance(signature.return_type, Hashable)
        return MethodMeta(response_type=get_type_adapter(signature.return_type))

    def _parse_payload(self, from_response: Response) -> Any:
        if self._raise_for_status:
            from_response.raise_for_status()
        try:
            return from_response.json()
        except ValueError:
            return {}  # FIXME
