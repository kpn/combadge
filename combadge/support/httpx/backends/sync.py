from typing import Any, Type

from httpx import Client, HTTPError, Response
from pydantic import BaseModel, parse_obj_as

from combadge.core.binder import BaseBoundService, Signature
from combadge.core.errors import CombadgeBackendError, CombadgeValidationError
from combadge.core.interfaces import SupportsBindServiceMethod, SupportsServiceMethodCall
from combadge.core.request import build_request
from combadge.core.typevars import ResponseT
from combadge.support.rest.request import Request


class HttpxBackend(SupportsBindServiceMethod):
    """
    HTTPX backend for REST APIs.

    See Also:
        - https://www.python-httpx.org/
    """

    _client: Client
    __slots__ = ("_client",)

    def __init__(self, client: Client) -> None:  # noqa: D107
        self._client = client

    def __call__(self, request: Request, response_type: Type[ResponseT]) -> ResponseT:
        """Call the backend."""
        json = body.json(by_alias=True) if (body := request.body) is not None else None
        try:
            response: Response = self._client.request(
                request.method,
                request.path,
                json=json,
                params=request.query_params,
            )
            response.raise_for_status()
        except HTTPError as e:
            raise CombadgeBackendError from e
        with CombadgeValidationError.wrap():
            return parse_obj_as(response_type, response.json())

    def bind_method(self, signature: Signature) -> SupportsServiceMethodCall:  # noqa: D102
        def resolved_method(service: BaseBoundService, *args: Any, **kwargs: Any) -> BaseModel:
            request = build_request(Request, signature, service, args, kwargs)
            return self(request, signature.return_type)

        return resolved_method  # type: ignore[return-value]
