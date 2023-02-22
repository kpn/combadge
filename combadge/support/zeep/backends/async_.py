from __future__ import annotations

from typing import Any, Type

from pydantic import BaseModel
from zeep.exceptions import Fault
from zeep.proxy import AsyncOperationProxy, AsyncServiceProxy

from combadge.core.binder import BaseBoundService, Signature
from combadge.core.interfaces import CallServiceMethod, ProvidesBinder
from combadge.core.request import build_request
from combadge.core.typevars import ResponseT
from combadge.support.soap.request import Request
from combadge.support.soap.response import SoapFaultT
from combadge.support.zeep.backends.base import BaseZeepBackend


class ZeepBackend(BaseZeepBackend[AsyncServiceProxy, AsyncOperationProxy], ProvidesBinder):
    """Asynchronous Zeep service."""

    async def __call__(
        self,
        request: Request,
        response_type: Type[ResponseT],
        fault_type: Type[SoapFaultT],
    ) -> BaseModel:
        """
        Call the specified service method.

        Args:
            request: prepared request
            response_type: non-fault response model type
            fault_type: SOAP fault model type
        """
        operation = self._get_operation(request.operation_name)
        try:
            response = await operation(**request.body.dict(by_alias=True))
        except Fault as e:
            return self._parse_soap_fault(e, fault_type)
        return self._parse_response(response, response_type)

    @classmethod
    def bind_method(cls, signature: Signature) -> CallServiceMethod[ZeepBackend]:  # noqa: D102
        response_type, fault_type = cls._split_response_type(signature.return_type)

        async def bound_method(service: BaseBoundService[ZeepBackend], *args: Any, **kwargs: Any) -> BaseModel:
            request = build_request(Request, signature, service, args, kwargs)
            return await service.backend(request, response_type, fault_type)

        return bound_method  # type: ignore[return-value]

    binder = bind_method  # type: ignore[assignment]
