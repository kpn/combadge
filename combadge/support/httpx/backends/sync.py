from __future__ import annotations

from contextlib import AbstractContextManager, nullcontext
from typing import Any, Callable, Iterable, Tuple, Type

from httpx import Client, Response
from pydantic import BaseModel

from combadge.core.binder import BaseBoundService, Signature
from combadge.core.interfaces import CallServiceMethod, ProvidesBinder
from combadge.core.request import build_request
from combadge.core.typevars import ResponseT
from combadge.support.httpx.backends.base import BaseHttpxBackend
from combadge.support.rest.request import Request


class HttpxBackend(BaseHttpxBackend[Client], ProvidesBinder):
    """
    Sync HTTPX backend for REST APIs.

    See Also:
        - <https://www.python-httpx.org/>
    """

    __slots__ = ("_request_with",)

    def __init__(  # noqa: D107
        self,
        client: Client,
        *,
        request_with: Callable[[], AbstractContextManager] = nullcontext,
    ) -> None:
        super().__init__(client=client)
        self._request_with = request_with

    def __call__(
        self,
        request: Request,
        response_type: Type[ResponseT],
        response_marks: Iterable[Tuple[str, Callable[[Response], Any]]],
    ) -> ResponseT:
        """Call the backend."""
        response: Response = self._client.request(
            request.method,
            request.path,
            json=request.body_dict(),
            params=request.query_params,
        )
        response.raise_for_status()
        return self._parse_response(response, response_type, response_marks)

    @classmethod
    def bind_method(cls, signature: Signature) -> CallServiceMethod[HttpxBackend]:  # noqa: D102
        response_marks = cls._bind_response_markers(signature.response_markers)

        def bound_method(service: BaseBoundService[HttpxBackend], *args: Any, **kwargs: Any) -> BaseModel:
            request = build_request(Request, signature, service, args, kwargs)
            with service.backend._request_with():
                return service.backend(request, signature.return_type, response_marks)

        return bound_method  # type: ignore[return-value]

    binder = bind_method  # type: ignore[assignment]
