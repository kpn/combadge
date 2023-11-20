from __future__ import annotations

from types import TracebackType
from typing import Any

from httpx import Client, Response
from pydantic import TypeAdapter
from typing_extensions import Self

from combadge.core.backend import ServiceContainer
from combadge.core.binder import BaseBoundService
from combadge.core.errors import BackendError
from combadge.core.interfaces import ServiceMethod
from combadge.core.signature import Signature
from combadge.support.http.request import Request
from combadge.support.httpx.backends.base import BaseHttpxBackend


class HttpxBackend(BaseHttpxBackend[Client], ServiceContainer):
    """Sync HTTPX backend."""

    __slots__ = ("_client", "_service_cache", "_raise_for_status")

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
        ServiceContainer.__init__(self)

    def bind_method(self, signature: Signature) -> ServiceMethod[HttpxBackend]:  # noqa: D102
        backend = self
        response_type = TypeAdapter(signature.return_type)

        def bound_method(self: BaseBoundService[HttpxBackend], *args: Any, **kwargs: Any) -> Any:
            request = signature.build_request(Request, self, args, kwargs)
            with BackendError:
                response: Response = backend._client.request(
                    request.get_method(),
                    request.get_url_path(),
                    json=request.payload,
                    data=request.form_data,
                    params=request.query_params,
                    headers=request.headers,
                )
                payload = backend._parse_payload(response)
            return signature.apply_response_markers(response, payload, response_type)

        return bound_method  # type: ignore[return-value]

    binder = bind_method  # type: ignore[assignment]

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
