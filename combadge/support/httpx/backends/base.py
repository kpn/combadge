from __future__ import annotations

from typing import Any, Generic, TypeVar

from httpx import AsyncClient, Client, Response

from combadge.core.interfaces import ProvidesBinder
from combadge.core.signature import Signature

_ClientT = TypeVar("_ClientT", Client, AsyncClient)


class BaseHttpxBackend(ProvidesBinder, Generic[_ClientT]):
    """[HTTPX](https://www.python-httpx.org/) client support."""

    _client: _ClientT

    def __init__(self, client: _ClientT, *, raise_for_status: bool = True) -> None:  # noqa: D107
        self._client = client
        self._raise_for_status = raise_for_status

    def _parse_response(self, from_response: Response, signature: Signature) -> Any:
        try:
            json_ = from_response.json()
        except ValueError:
            json_ = {}
        if self._raise_for_status:
            from_response.raise_for_status()
        return signature.apply_response_markers(from_response, json_, signature.return_type)
