from __future__ import annotations

from types import TracebackType
from typing import Any

from httpx import AsyncClient
from typing_extensions import Self

from combadge.core.binder import BaseBoundService
from combadge.core.container import ServiceContainerMixin
from combadge.core.errors import BackendError
from combadge.core.interfaces import ServiceMethod
from combadge.core.signature import Signature
from combadge.support.http.request import Request
from combadge.support.httpx.backends.base import BaseHttpxBackend, MethodMeta


class HttpxBackend(BaseHttpxBackend[AsyncClient], ServiceContainerMixin):
    """Async HTTPX backend."""

    __slots__ = ("_client", "_service_cache", "_raise_for_status")

    def __init__(
        self,
        client: AsyncClient,
        *,
        raise_for_status: bool = True,
    ) -> None:
        """
        Instantiate the backend.

        Args:
            client: [HTTPX client](https://www.python-httpx.org/advanced/#client-instances)
            raise_for_status: if `True`, automatically call `raise_for_status()`
        """
        BaseHttpxBackend.__init__(self, client, raise_for_status=raise_for_status)
        ServiceContainerMixin.__init__(self)

    def bind_method(self, signature: Signature) -> ServiceMethod[Self]:  # noqa: D102
        meta = self.inspect(signature)

        async def bound_method(self: BaseBoundService[Self], *args: Any, **kwargs: Any) -> Any:
            request = signature.build_request(Request, self, args, kwargs)
            with BackendError:
                return await self.__combadge_backend__(request, meta)

        return bound_method  # type: ignore[return-value]

    async def __call__(self, request: Request, meta: MethodMeta) -> Any:  # noqa: D102
        response = await self._client.request(
            request.get_method(),
            request.get_url_path(),
            json=request.payload,
            data=request.form_data,
            params=request.query_params,
            headers=request.http_headers,
        )
        return self._parse_response(meta, response)

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
