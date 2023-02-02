from abc import ABC
from typing import Any, Generic, Tuple, Type, TypeVar, Union
from warnings import warn

from pydantic import BaseModel, parse_obj_as
from typing_extensions import get_args as get_type_args
from typing_extensions import get_origin as get_type_origin
from zeep.exceptions import Fault
from zeep.helpers import serialize_object
from zeep.proxy import AsyncOperationProxy, AsyncServiceProxy, OperationProxy, ServiceProxy

from combadge.core.binder import BaseBoundService
from combadge.core.interfaces import SupportsBindMethod, SupportsMethodCall
from combadge.core.response import SuccessfulResponse
from combadge.core.typevars import ResponseT
from combadge.core.warnings import ServiceCallWarning
from combadge.support.soap.response import BaseSoapFault, SoapFaultT

ServiceProxyT = TypeVar("ServiceProxyT", bound=ServiceProxy)
"""
Specific service proxy type returned by a Zeep client.

See Also:
    - https://docs.python-zeep.org/en/master/client.html#the-serviceproxy-object
"""

OperationProxyT = TypeVar("OperationProxyT", bound=OperationProxy)


class BaseZeepBackend(ABC, Generic[ServiceProxyT, OperationProxyT]):
    """Base class for the sync and async backends. Not intended for a direct use."""

    __slots__ = ("_service",)

    def __init__(self, service: ServiceProxyT) -> None:
        """Instantiate the backend."""
        self._service = service

    @staticmethod
    def _validate_operation_name(method: Any) -> str:
        """Validate and return the operation name assigned to the method."""
        try:
            return method.__soap_operation_name__
        except AttributeError as e:
            raise ValueError("Zeep resolver requires each method to have a SOAP operation name") from e

    @staticmethod
    def _split_response_type(response_type: Type[Any]) -> Tuple[Type[BaseModel], Type[BaseSoapFault]]:
        """
        Split the response type into non-faults and faults.

        SOAP faults are handled separately, so we need to extract them from the annotated
        response type.
        """

        if get_type_origin(response_type) is Union:  # noqa: SIM108
            return_types = get_type_args(response_type)
        else:
            return_types = (response_type,)

        fault_type = BaseSoapFault

        response_type: Any = ...
        for return_type in return_types:
            if isinstance(return_type, type) and issubclass(return_type, BaseSoapFault):
                fault_type = Union[return_type, fault_type]  # type: ignore
            elif response_type is Ellipsis:
                response_type = return_type
            else:
                response_type = Union[response_type, return_type]  # type: ignore

        if response_type is Ellipsis:
            response_type = SuccessfulResponse

        return response_type, fault_type

    def _get_operation(self, name: str) -> OperationProxyT:
        """Get an operation by its name."""
        try:
            return self._service[name]
        except AttributeError as e:
            raise RuntimeError(f"available operations are: {dir(self._service)}") from e

    @staticmethod
    def _validate_call_args(body: Any, *args: Any, **kwargs: Any) -> None:
        if not isinstance(body, BaseModel):
            raise TypeError(f"the body is not an instance of `BaseModel`, got `{type(body)}`")
        if args or kwargs:
            warn(ServiceCallWarning(f"{len(args)} positional args and {len(kwargs)} are ignored"))

    @staticmethod
    def _parse_response(value: Any, response_type: Type[ResponseT]) -> ResponseT:
        """Parse the response value using the generic response types."""
        return parse_obj_as(response_type, serialize_object(value, dict))

    @staticmethod
    def _parse_soap_fault(exception: Fault, fault_type: Type[SoapFaultT]) -> SoapFaultT:
        """Parse the SOAP fault."""
        return parse_obj_as(fault_type, exception.__dict__)


class ZeepBackend(BaseZeepBackend[ServiceProxy, OperationProxy], SupportsBindMethod):
    """Synchronous Zeep service. When updating, make sure to update the async variant too."""

    def __call__(
        self,
        operation_name: str,
        request: BaseModel,
        response_type: Type[ResponseT],
        fault_type: Type[SoapFaultT],
    ) -> Union[ResponseT, SoapFaultT]:
        """
        Call the specified service method.

        Args:
            operation_name: SOAP operation name per WSDL
            request: request body
            response_type: non-fault response model type
            fault_type: SOAP fault model type
        """
        operation = self._get_operation(operation_name)
        try:
            response = operation(**request.dict(by_alias=True))
        except Fault as e:
            return self._parse_soap_fault(e, fault_type)
        return self._parse_response(response, response_type)

    def bind_method(  # noqa: D102
        self,
        response_type: Type[Union[BaseModel, BaseSoapFault]],
        method: SupportsMethodCall,
    ) -> SupportsMethodCall:
        soap_name = self._validate_operation_name(method)
        clean_response_type, fault_type = self._split_response_type(response_type)

        def resolved_method(
            _service: BaseBoundService,
            body: Any,
            *args: Any,
            **kwargs: Any,
        ) -> BaseModel:
            self._validate_call_args(body, *args, **kwargs)
            return self(soap_name, body, clean_response_type, fault_type)

        return resolved_method  # type: ignore[return-value]


class ZeepBackendAsync(BaseZeepBackend[AsyncServiceProxy, AsyncOperationProxy], SupportsBindMethod):
    """Asynchronous Zeep service. When updating, make sure to update the sync variant too."""

    async def __call__(
        self,
        operation_name: str,
        request: BaseModel,
        response_type: Type[ResponseT],
        fault_type: Type[SoapFaultT],
    ) -> BaseModel:
        """
        Call the specified service method.

        Args:
            operation_name: SOAP operation name per WSDL
            request: request body
            response_type: non-fault response model type
            fault_type: SOAP fault model type
        """
        operation = self._get_operation(operation_name)
        try:
            response = await operation(**request.dict(by_alias=True))
        except Fault as e:
            return self._parse_soap_fault(e, fault_type)
        return self._parse_response(response, response_type)

    def bind_method(  # noqa: D102
        self,
        response_type: Type[Union[BaseModel, BaseSoapFault]],
        method: SupportsMethodCall,
    ) -> SupportsMethodCall:
        soap_name = self._validate_operation_name(method)
        clean_response_type, fault_type = self._split_response_type(response_type)

        async def resolved_method(
            _service: BaseBoundService,
            body: Any,
            *args: Any,
            **kwargs: Any,
        ) -> BaseModel:
            self._validate_call_args(body, *args, **kwargs)
            return await self(soap_name, body, clean_response_type, fault_type)

        return resolved_method  # type: ignore[return-value]
