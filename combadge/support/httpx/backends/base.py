from __future__ import annotations

from typing import Any, Generic, TypeVar

from httpx import AsyncClient, Client, Response

from combadge.core.interfaces import ProvidesBinder

_ClientT = TypeVar("_ClientT", Client, AsyncClient)


class BaseHttpxBackend(ProvidesBinder, Generic[_ClientT]):
    """[HTTPX](https://www.python-httpx.org/) client support."""

    _client: _ClientT

    def __init__(self, client: _ClientT, *, raise_for_status: bool = True) -> None:  # noqa: D107
        self._client = client
        self._raise_for_status = raise_for_status

    def _parse_payload(self, from_response: Response) -> Any:
        if self._raise_for_status:
            from_response.raise_for_status()
        try:
            return from_response.json()
        except ValueError:
            return {}  # FIXME
