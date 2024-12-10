from __future__ import annotations

from abc import ABC
from typing import Any, Generic, TypeVar

from httpx import AsyncClient, Client, Response

from combadge.core.backend import BaseBackend

_ClientT = TypeVar("_ClientT", Client, AsyncClient)


class BaseHttpxBackend(BaseBackend, Generic[_ClientT], ABC):
    """[HTTPX](https://www.python-httpx.org/) client support."""

    __slots__ = ("_service_cache", "_client", "_raise_for_status")

    def __init__(self, client: _ClientT, *, raise_for_status: bool = True) -> None:  # noqa: D107
        super().__init__()
        self._client: _ClientT = client
        self._raise_for_status = raise_for_status

    def _parse_payload(self, from_response: Response) -> Any:
        if self._raise_for_status:
            from_response.raise_for_status()
        try:
            return from_response.json()
        except ValueError:
            return {}  # FIXME
