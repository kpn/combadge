from __future__ import annotations

from contextlib import AbstractContextManager, nullcontext
from typing import Any, Callable, Type

from httpx import Client, Response
from pydantic import BaseModel

from combadge.core.binder import BaseBoundService
from combadge.core.interfaces import CallServiceMethod
from combadge.core.request import build_request
from combadge.core.signature import Signature
from combadge.core.typevars import ResponseT
from combadge.support.httpx.backends.base import BaseHttpxBackend
from combadge.support.rest.request import Request
from combadge.support.shared.sync import SupportsRequestWith


class HttpxBackend(BaseHttpxBackend[Client], SupportsRequestWith[Request]):
    """Sync HTTPX backend for REST APIs."""

    __slots__ = ("_client", "_request_with", "_raise_for_status")

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

    def __call__(self, request: Request, response_type: Type[ResponseT]) -> ResponseT:
        """
        Call the backend and parse a response.

        !!! info ""
            One does not normally need to call this directly, unless writing a custom binder.
        """
        response: Response = self._client.request(
            request.method,
            request.path,
            json=request.to_json_dict(),
            data=request.to_form_data(),
            params=request.query_params,
        )
        if self._raise_for_status:
            response.raise_for_status()
        return self._parse_response(response, response_type)

    @classmethod
    def bind_method(cls, signature: Signature) -> CallServiceMethod[HttpxBackend]:  # noqa: D102
        def bound_method(self: BaseBoundService[HttpxBackend], *args: Any, **kwargs: Any) -> BaseModel:
            request = build_request(Request, signature, self, args, kwargs)
            with self.backend._request_with(request):
                return self.backend(request, signature.return_type)

        return bound_method  # type: ignore[return-value]

    binder = bind_method  # type: ignore[assignment]
