from __future__ import annotations

from contextlib import AbstractContextManager, nullcontext
from types import TracebackType
from typing import Any, Callable, Optional, Type, Union

from pydantic import BaseModel
from typing_extensions import Self
from zeep.exceptions import Fault
from zeep.proxy import OperationProxy, ServiceProxy

from combadge.core.backend import ServiceContainer
from combadge.core.binder import BaseBoundService
from combadge.core.interfaces import CallServiceMethod
from combadge.core.request import build_request
from combadge.core.signature import Signature
from combadge.core.typevars import ResponseT
from combadge.support.shared.sync import SupportsRequestWith
from combadge.support.soap.request import Request
from combadge.support.soap.response import SoapFaultT
from combadge.support.zeep.backends.base import BaseZeepBackend


class ZeepBackend(BaseZeepBackend[ServiceProxy, OperationProxy], SupportsRequestWith[Request], ServiceContainer):
    """Synchronous Zeep service."""

    __slots__ = ("_service", "_request_with", "_service_cache")

    def __init__(
        self,
        service: ServiceProxy,
        *,
        request_with: Callable[[Any], AbstractContextManager] = nullcontext,
    ) -> None:
        """
        Instantiate the backend.

        Args:
            service: [service proxy object](https://docs.python-zeep.org/en/master/client.html#the-serviceproxy-object)
            request_with: an optional context manager getter to wrap each request into
        """
        BaseZeepBackend.__init__(self, service)
        SupportsRequestWith.__init__(self, request_with)
        ServiceContainer.__init__(self)

    def __call__(
        self,
        request: Request,
        response_type: Type[ResponseT],
        fault_type: Type[SoapFaultT],
    ) -> Union[ResponseT, SoapFaultT]:
        """
        Call the specified service method.

        Args:
            request: prepared request
            response_type: non-fault response model type
            fault_type: SOAP fault model type
        """
        operation = self._get_operation(request.operation_name)
        try:
            response = operation(**request.body.dict(by_alias=True))
        except Fault as e:
            return self._parse_soap_fault(e, fault_type)
        return self._parse_response(response, response_type)

    @classmethod
    def bind_method(cls, signature: Signature) -> CallServiceMethod[ZeepBackend]:  # noqa: D102
        response_type, fault_type = cls._split_response_type(signature.return_type)

        def bound_method(self: BaseBoundService[ZeepBackend], *args: Any, **kwargs: Any) -> BaseModel:
            request = build_request(Request, signature, self, args, kwargs)
            with self.backend._request_with(request):
                return self.backend(request, response_type, fault_type)

        return bound_method  # type: ignore[return-value]

    binder = bind_method  # type: ignore[assignment]

    def __enter__(self) -> Self:
        self._service = self._service.__enter__()
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Any:
        return self._service.__exit__(exc_type, exc_value, traceback)
