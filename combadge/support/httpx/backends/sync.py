from __future__ import annotations

from collections.abc import Hashable
from types import TracebackType
from typing import Any, cast

from httpx import Client, Response
from pydantic import TypeAdapter
from typing_extensions import Self, override

from combadge._helpers.pydantic import get_type_adapter
from combadge.core.binder import BaseBoundService
from combadge.core.errors import BackendError
from combadge.core.interfaces import ServiceMethod
from combadge.core.signature import Signature
from combadge.support.http.request import Request
from combadge.support.httpx.backends.base import BaseHttpxBackend


class HttpxBackend(BaseHttpxBackend[Client]):
    """Sync HTTPX backend."""

    __slots__ = ("_service_cache", "_client", "_raise_for_status")

    def __init__(
        self,
        client: Client,
        *,
        raise_for_status: bool = True,
    ) -> None:
        """
        Instantiate the backend.

        Args:
            client: [HTTPX client](https://www.python-httpx.org/advanced/#client-instances)
            raise_for_status: automatically call `raise_for_status()`
        """
        BaseHttpxBackend.__init__(self, client, raise_for_status=raise_for_status)

    @classmethod
    @override
    def bind_method(cls, signature: Signature) -> ServiceMethod[HttpxBackend]:  # noqa: D102
        response_type: TypeAdapter[Any] = get_type_adapter(cast(Hashable, signature.return_type))

        def bound_method(self: BaseBoundService[HttpxBackend], *args: Any, **kwargs: Any) -> Any:
            request = signature.build_request(Request, self, args, kwargs)
            with BackendError:
                response: Response = self.__combadge_backend__._client.request(
                    request.get_method(),
                    request.get_url_path(),
                    json=request.payload,
                    data=request.form_data,
                    params=request.query_params,
                    headers=request.http_headers,
                )
                payload = self.__combadge_backend__._parse_payload(response)
            return signature.apply_response_markers(response, payload, response_type)

        return bound_method  # type: ignore[return-value]

    def __enter__(self) -> Self:
        self._client = self._client.__enter__()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> Any:
        return self._client.__exit__(exc_type, exc_value, traceback)
