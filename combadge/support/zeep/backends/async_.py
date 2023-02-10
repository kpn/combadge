from typing import Any, Type

from pydantic import BaseModel
from zeep.exceptions import Fault
from zeep.proxy import AsyncOperationProxy, AsyncServiceProxy

from combadge.core.binder import BaseBoundService, Signature
from combadge.core.interfaces import SupportsBindServiceMethod, SupportsServiceMethodCall
from combadge.core.request import build_request
from combadge.core.typevars import ResponseT
from combadge.support.soap.request import Request
from combadge.support.soap.response import SoapFaultT
from combadge.support.zeep.backends.base import BaseZeepBackend


class ZeepBackend(BaseZeepBackend[AsyncServiceProxy, AsyncOperationProxy], SupportsBindServiceMethod):
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

    def bind_method(self, signature: Signature) -> SupportsServiceMethodCall:  # noqa: D102
        response_type, fault_type = self._split_response_type(signature.return_type)

        async def resolved_method(service: BaseBoundService, *args: Any, **kwargs: Any) -> BaseModel:
            request = build_request(Request, signature, service, args, kwargs)
            return await self(request, response_type, fault_type)

        return resolved_method  # type: ignore[return-value]
