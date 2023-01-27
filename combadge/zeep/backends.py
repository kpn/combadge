from abc import ABC, abstractmethod
from os import PathLike, fspath
from typing import Any, Generic, List, Optional, Tuple, Type, TypeVar, Union, cast

from pydantic import parse_obj_as
from typing_extensions import get_args as get_type_args
from typing_extensions import get_origin as get_type_origin
from zeep.helpers import serialize_object

from combadge.binder import BaseBoundService
from combadge.interfaces import RequestT, SupportsBindMethod, SupportsMethodCall

try:
    import httpx
except ImportError:
    httpx = None  # type: ignore

from requests import Session
from requests.auth import HTTPBasicAuth
from zeep import Client, Plugin, Settings, Transport
from zeep.exceptions import Fault
from zeep.proxy import OperationProxy, ServiceProxy

from combadge.response import ResponseT, SuccessfulResponse
from combadge.zeep.response import BaseSoapFault, SoapFaultT

AuthT = TypeVar("AuthT")
"""Authentication parameter type."""

ServiceProxyT = TypeVar("ServiceProxyT", bound=ServiceProxy)
"""
Specific service proxy type returned by a Zeep client.

See Also:
    - https://docs.python-zeep.org/en/master/client.html#the-serviceproxy-object
"""

OperationProxyT = TypeVar("OperationProxyT", bound=OperationProxy)


class BaseZeepBackend(ABC, Generic[AuthT, ServiceProxyT, OperationProxyT]):
    """Base class for the sync and async backends. Not intended for a direct use."""

    def __init__(
        self,
        *,
        wsdl_path: PathLike,
        port: Optional[Tuple[str, str]] = None,
        auth: Optional[AuthT] = None,
        timeout_secs: Optional[int] = None,
        verify_ssl: bool = True,
        cert: Optional[Tuple[str, str]] = None,
        plugins: Optional[List[Plugin]] = None,
    ) -> None:
        """Instantiate the backend."""
        self._service = self._create_service(
            wsdl_path=fspath(wsdl_path),
            port=port,
            auth=auth,
            verify_ssl=verify_ssl,
            cert=cert,
            timeout=timeout_secs,
            plugins=plugins,
        )

    @abstractmethod
    def _create_service(
        self,
        *,
        wsdl_path: str,
        port: Optional[Tuple[str, str]],
        auth: Optional[AuthT],
        verify_ssl: bool,
        cert: Optional[Tuple[str, str]],
        timeout: Optional[int],
        plugins: Optional[List[Plugin]],
    ) -> ServiceProxyT:
        """Instantiate a service specific to the sync/async client."""
        raise NotImplementedError

    @staticmethod
    def _validate_operation_name(method: Any) -> str:
        try:
            return method.__soap_operation_name__
        except AttributeError as e:
            raise ValueError("Zeep resolver requires each method to have a SOAP operation name") from e

    @staticmethod
    def _split_response_type(response_type: Any) -> Tuple[Any, Any]:
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

        response_type = ...
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
        try:
            return self._service[name]
        except AttributeError as e:
            raise RuntimeError(f"available operations are: {dir(self._service)}") from e

    @staticmethod
    def _parse_response(value: Any, response_type: Type[ResponseT]) -> ResponseT:
        """Parse the response value using the generic response types."""
        return parse_obj_as(response_type, serialize_object(value, dict))

    @staticmethod
    def _parse_soap_fault(exception: Fault, fault_type: Type[SoapFaultT]) -> SoapFaultT:
        """Parse the SOAP fault."""
        return parse_obj_as(fault_type, exception.__dict__)


ZEEP_SETTINGS = Settings(xsd_ignore_sequence_order=True)
"""Shared Zeep client settings."""


class ZeepBackend(
    BaseZeepBackend[HTTPBasicAuth, ServiceProxy, OperationProxy],
    SupportsBindMethod,
):
    """Synchronous Zeep service. When updating, make sure to update the async variant too."""

    def __call__(
        self,
        operation_name: str,
        request: RequestT,
        response_type: Type[ResponseT],
        fault_type: Type[SoapFaultT],
    ) -> Union[ResponseT, SoapFaultT]:
        """Call the specified service method."""
        operation = self._get_operation(operation_name)
        try:
            response = operation(**request.dict(by_alias=True))
        except Fault as e:
            return self._parse_soap_fault(e, fault_type)
        return self._parse_response(response, response_type)

    def _create_service(
        self,
        *,
        wsdl_path: str,
        port: Optional[Tuple[str, str]],
        auth: Optional[HTTPBasicAuth],
        verify_ssl: bool,
        cert: Optional[Tuple[str, str]],
        timeout: Optional[int],
        plugins: Optional[List[Plugin]],
    ) -> ServiceProxy:
        session = Session()
        session.auth = auth
        session.verify = verify_ssl
        session.cert = cert

        transport = Transport(session=session, timeout=timeout)
        client = Client(wsdl=wsdl_path, transport=transport, settings=ZEEP_SETTINGS, plugins=plugins)

        if port:
            binding_name, address = port
            return client.create_service(binding_name, address)
        else:
            return client.service

    def bind_method(  # noqa: D102
        self,
        _request_type: Type[RequestT],
        response_type: Type[ResponseT],
        method: Any,
    ) -> SupportsMethodCall[RequestT, ResponseT]:
        soap_name = self._validate_operation_name(method)
        response_type, fault_type = self._split_response_type(response_type)

        # noinspection PyShadowingNames
        def resolved_method(_service: BaseBoundService, request: RequestT) -> ResponseT:
            return cast(ResponseT, self(soap_name, request, response_type, fault_type))

        return resolved_method


if httpx is not None:
    from httpx import BasicAuth
    from zeep import AsyncClient
    from zeep.proxy import AsyncOperationProxy, AsyncServiceProxy
    from zeep.transports import AsyncTransport

    class ZeepBackendAsync(
        BaseZeepBackend[BasicAuth, AsyncServiceProxy, AsyncOperationProxy],
        SupportsBindMethod,
    ):
        """Asynchronous Zeep service. When updating, make sure to update the sync variant too."""

        async def __call__(
            self,
            operation_name: str,
            request: RequestT,
            response_type: Type[ResponseT],
            fault_type: Type[SoapFaultT],
        ) -> Union[ResponseT, BaseSoapFault]:
            """Call the specified service method."""
            operation = self._get_operation(operation_name)
            try:
                response = await operation(**request.dict(by_alias=True))
            except Fault as e:
                return self._parse_soap_fault(e, fault_type)
            return self._parse_response(response, response_type)

        def _create_service(
            self,
            *,
            wsdl_path: str,
            port: Optional[Tuple[str, str]],
            auth: Optional[BasicAuth],
            verify_ssl: bool,
            cert: Optional[Tuple[str, str]],
            timeout: Optional[int],
            plugins: Optional[List[Plugin]],
        ) -> AsyncServiceProxy:
            inner_client = httpx.AsyncClient(timeout=timeout, verify=verify_ssl, cert=cert, auth=auth)
            transport = AsyncTransport(client=inner_client)
            client = AsyncClient(wsdl=wsdl_path, transport=transport, settings=ZEEP_SETTINGS, plugins=plugins)

            if port:
                binding_name, address = port
                return client.create_service(binding_name, address)
            else:
                return client.service

        def bind_method(  # noqa: D102
            self,
            _request_type: Type[RequestT],
            response_type: Type[ResponseT],
            method: Any,
        ) -> SupportsMethodCall[RequestT, ResponseT]:
            soap_name = self._validate_operation_name(method)
            response_type, fault_type = self._split_response_type(response_type)

            # noinspection PyShadowingNames
            async def resolved_method(_service: BaseBoundService, request: RequestT) -> ResponseT:
                return cast(ResponseT, await self(soap_name, request, response_type, fault_type))

            return resolved_method
