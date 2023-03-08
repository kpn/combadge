from __future__ import annotations

import sys
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import Any, AsyncGenerator, Callable, Type

from httpx import AsyncClient, Response
from pydantic import BaseModel

from combadge.core.binder import BaseBoundService
from combadge.core.interfaces import CallServiceMethod, ProvidesBinder
from combadge.core.request import build_request
from combadge.core.signature import Signature
from combadge.core.typevars import ResponseT
from combadge.support.httpx.backends.base import BaseHttpxBackend
from combadge.support.rest.request import Request

if sys.version_info >= (3, 10):
    from contextlib import nullcontext as asyncnullcontext
else:

    @asynccontextmanager
    async def asyncnullcontext() -> AsyncGenerator[None, None]:
        yield None


class HttpxBackend(BaseHttpxBackend[AsyncClient], ProvidesBinder):
    """Async HTTPX backend for REST APIs."""

    __slots__ = ("_request_with",)

    def __init__(
        self,
        client: AsyncClient,
        *,
        request_with: Callable[[], AbstractAsyncContextManager] = asyncnullcontext,
    ) -> None:
        """
        Instantiate the backend.

        Args:
            client: [HTTPX client](https://www.python-httpx.org/advanced/#client-instances)
            request_with: an optional context manager getter to wrap each request into
        """
        super().__init__(client=client)
        self._request_with = request_with

    async def __call__(self, request: Request, response_type: Type[ResponseT]) -> ResponseT:
        """
        Call the backend and parse a response.

        !!! info ""
            One does not normally need to call this directly, unless writing a custom binder.
        """
        response: Response = await self._client.request(
            request.method,
            request.path,
            json=request.json_dict(),
            params=request.query_params,
        )
        response.raise_for_status()
        return self._parse_response(response, response_type)

    @classmethod
    def bind_method(cls, signature: Signature) -> CallServiceMethod[HttpxBackend]:  # noqa: D102
        async def bound_method(self: BaseBoundService[HttpxBackend], *args: Any, **kwargs: Any) -> BaseModel:
            request = build_request(Request, signature, self, args, kwargs)
            async with self.backend._request_with():
                return await self.backend(request, signature.return_type)

        return bound_method  # type: ignore[return-value]

    binder = bind_method  # type: ignore[assignment]
