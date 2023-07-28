from __future__ import annotations

from collections.abc import Collection
from contextlib import AbstractAsyncContextManager
from os import PathLike, fspath
from ssl import SSLContext
from types import TracebackType
from typing import Any, Callable

import httpx
from pydantic import BaseModel
from typing_extensions import Self
from zeep import AsyncClient, Plugin
from zeep.exceptions import Fault
from zeep.proxy import AsyncOperationProxy, AsyncServiceProxy
from zeep.transports import AsyncTransport
from zeep.wsse import UsernameToken

from combadge.core.backend import ServiceContainer
from combadge.core.binder import BaseBoundService
from combadge.core.interfaces import CallServiceMethod
from combadge.core.request import build_request
from combadge.core.signature import Signature
from combadge.core.typevars import ResponseT
from combadge.support.shared.async_ import SupportsRequestWith
from combadge.support.shared.contextlib import asyncnullcontext
from combadge.support.soap.request import Request
from combadge.support.soap.response import SoapFaultT
from combadge.support.zeep.backends.base import BaseZeepBackend, ByBindingName, ByServiceName


class ZeepBackend(
    BaseZeepBackend[AsyncServiceProxy, AsyncOperationProxy],
    SupportsRequestWith[Request],
    ServiceContainer,
):
    """Asynchronous Zeep service."""

    __slots__ = ("_service", "_request_with", "_service_cache")

    @classmethod
    def with_params(
        cls,
        wsdl_path: PathLike,
        *,
        service: ByBindingName | ByServiceName | None = None,
        plugins: Collection[Plugin] | None = None,
        load_timeout: float | None = None,
        operation_timeout: float | None = None,
        wsse: UsernameToken | None = None,
        verify_ssl: PathLike | bool | SSLContext = True,
        cert: PathLike | tuple[PathLike, PathLike | None] | tuple[PathLike, PathLike | None, str | None] | None = None,
    ) -> ZeepBackend:
        """
        Instantiate the backend using a set of the most common parameters.

        Using the `__init__()` may become quite wordy, so this method simplifies typical use cases.
        """
        verify = verify_ssl if isinstance(verify_ssl, (bool, SSLContext)) else fspath(verify_ssl)

        if isinstance(cert, tuple):
            cert_file = cert[0]
            key_file = cert[1]
            password = cert[2] if len(cert) == 3 else None  # type: ignore[misc]
            cert_ = (fspath(cert_file), fspath(key_file) if key_file else None, password)
        elif cert is not None:
            cert_ = fspath(cert)
        else:
            cert_ = None

        transport = AsyncTransport(
            timeout=None,  # overloaded
            client=httpx.AsyncClient(timeout=operation_timeout, verify=verify, cert=cert_),
            wsdl_client=httpx.Client(timeout=load_timeout, verify=verify, cert=cert_),
        )

        client = AsyncClient(fspath(wsdl_path), wsse=wsse, plugins=plugins, transport=transport)
        if service is None:
            service_proxy = client.service
        elif isinstance(service, ByServiceName):
            service_proxy = client.bind(service.service_name, service.port_name)
        elif isinstance(service, ByBindingName):
            # `create_service()` creates a sync service proxy, work around:
            service_proxy = AsyncServiceProxy(
                client,
                client.wsdl.bindings[service.binding_name],
                address=service.address,
            )
        else:
            raise TypeError(type(service))
        return cls(service_proxy)

    def __init__(
        self,
        service: AsyncServiceProxy,
        *,
        request_with: Callable[[Any], AbstractAsyncContextManager] = asyncnullcontext,
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

    async def __call__(
        self,
        request: Request,
        response_type: type[ResponseT],
        fault_type: type[SoapFaultT],
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

        async def bound_method(self: BaseBoundService[ZeepBackend], *args: Any, **kwargs: Any) -> BaseModel:
            request = build_request(Request, signature, self, args, kwargs)
            async with self.backend._request_with(request):
                return await self.backend(request, response_type, fault_type)

        return bound_method  # type: ignore[return-value]

    binder = bind_method  # type: ignore[assignment]

    async def __aenter__(self) -> Self:
        self._service = await self._service.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> Any:
        return await self._service.__aexit__(exc_type, exc_value, traceback)
