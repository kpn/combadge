from __future__ import annotations

from contextlib import AbstractContextManager, nullcontext
from types import TracebackType
from typing import Any, Callable

from httpx import Client, Response
from pydantic import BaseModel, RootModel
from typing_extensions import Self

from combadge.core.backend import ServiceContainer
from combadge.core.binder import BaseBoundService
from combadge.core.interfaces import CallServiceMethod
from combadge.core.signature import Signature
from combadge.core.typevars import ResponseT
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

    def __call__(self, request: Request, response_type: type[ResponseT]) -> ResponseT:
        """
        Call the backend and parse a response.

        !!! info ""
            One does not normally need to call this directly, unless writing a custom binder.
        """
        response: Response = self._client.request(
            request.get_method(),
            request.get_url_path(),
            json=request.json_,
            data=request.form_data,
            params=request.query_params,
            headers=request.headers,
        )
        if self._raise_for_status:
            response.raise_for_status()
        return self._parse_response(response, response_type)

    @staticmethod
    def bind_method(signature: Signature) -> CallServiceMethod[HttpxBackend]:  # noqa: D102
        # Return type may be anything, hence wrapping into `RootModel`.
        return_type = RootModel[signature.return_type]  # type: ignore[misc, name-defined]

        def bound_method(self: BaseBoundService[HttpxBackend], *args: Any, **kwargs: Any) -> BaseModel:
            request = Request(signature, self, args, kwargs)
            with self.backend._request_with(request):
                return self.backend(request, return_type).root

        return bound_method  # type: ignore[return-value]

    binder = bind_method

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
