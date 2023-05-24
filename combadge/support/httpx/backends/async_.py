from __future__ import annotations

from contextlib import AbstractAsyncContextManager
from types import TracebackType
from typing import Any, Callable

from httpx import AsyncClient, Response
from pydantic import BaseModel
from typing_extensions import Self

from combadge.core.backend import ServiceContainer
from combadge.core.binder import BaseBoundService
from combadge.core.interfaces import CallServiceMethod
from combadge.core.request import build_request
from combadge.core.signature import Signature
from combadge.core.typevars import ResponseT
from combadge.support.http.request import Request
from combadge.support.httpx.backends.base import BaseHttpxBackend
from combadge.support.shared.async_ import SupportsRequestWith
from combadge.support.shared.contextlib import asyncnullcontext


class HttpxBackend(BaseHttpxBackend[AsyncClient], SupportsRequestWith[Request], ServiceContainer):
    """Async HTTPX backend for REST APIs."""

    __slots__ = ("_client", "_request_with", "_service_cache", "_raise_for_status")

    def __init__(
        self,
        client: AsyncClient,
        *,
        request_with: Callable[[Any], AbstractAsyncContextManager] = asyncnullcontext,
        raise_for_status: bool = True,
    ) -> None:
        """
        Instantiate the backend.

        Args:
            client: [HTTPX client](https://www.python-httpx.org/advanced/#client-instances)
            request_with: an optional context manager getter to wrap each request into
            raise_for_status: automatically call `raise_for_status()`
        """
        BaseHttpxBackend.__init__(self, client, raise_for_status=raise_for_status)
        SupportsRequestWith.__init__(self, request_with)
        ServiceContainer.__init__(self)

    async def __call__(self, request: Request, response_type: type[ResponseT]) -> ResponseT:
        """
        Call the backend and parse a response.

        !!! info ""
            One does not normally need to call this directly, unless writing a custom binder.
        """
        response: Response = await self._client.request(
            request.method,
            request.path,
            json=request.json_,
            data=request.form_data,
            params=request.query_params,
            headers=request.headers,
        )
        if self._raise_for_status:
            response.raise_for_status()
        return self._parse_response(response, response_type)

    @classmethod
    def bind_method(cls, signature: Signature) -> CallServiceMethod[HttpxBackend]:  # noqa: D102
        async def bound_method(self: BaseBoundService[HttpxBackend], *args: Any, **kwargs: Any) -> BaseModel:
            request = build_request(Request, signature, self, args, kwargs)
            async with self.backend._request_with(request):
                return await self.backend(request, signature.return_type)

        return bound_method  # type: ignore[return-value]

    binder = bind_method  # type: ignore[assignment]

    async def __aenter__(self) -> Self:
        self._client = await self._client.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> Any:
        return await self._client.__aexit__(exc_type, exc_value, traceback)
