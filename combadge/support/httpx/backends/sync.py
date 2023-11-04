from __future__ import annotations

from contextlib import AbstractContextManager, nullcontext
from types import TracebackType
from typing import Any, Callable

from httpx import Client, Response
from pydantic import TypeAdapter
from typing_extensions import Self

from combadge.core.backend import ServiceContainer
from combadge.core.binder import BaseBoundService
from combadge.core.interfaces import ServiceMethod
from combadge.core.signature import Signature
from combadge.support.http.request import Request
from combadge.support.httpx.backends.base import BaseHttpxBackend
from combadge.support.shared.sync import SupportsRequestWith


class HttpxBackend(BaseHttpxBackend[Client], SupportsRequestWith[Request], ServiceContainer):
    """Sync HTTPX backend for REST APIs."""

    __slots__ = ("_client", "_request_with", "_service_cache", "_raise_for_status")

    def __init__(
        self,
        client: Client,
        *,
        request_with: Callable[[Any], AbstractContextManager] = nullcontext,
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

    def bind_method(self, signature: Signature) -> ServiceMethod[HttpxBackend]:  # noqa: D102
        backend = self
        response_type = TypeAdapter(signature.return_type)

        def bound_method(self: BaseBoundService[HttpxBackend], *args: Any, **kwargs: Any) -> Any:
            request = signature.build_request(Request, self, args, kwargs)
            with self.backend._request_with(request):
                response: Response = backend._client.request(
                    request.get_method(),
                    request.get_url_path(),
                    json=request.payload,
                    data=request.form_data,
                    params=request.query_params,
                    headers=request.headers,
                )
            return signature.apply_response_markers(response, backend._parse_response(response), response_type)

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
