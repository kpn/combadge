from __future__ import annotations

from collections.abc import Collection
from os import PathLike, fspath
from ssl import SSLContext
from types import TracebackType
from typing import Any

import httpx
from typing_extensions import Self
from zeep import AsyncClient, Plugin
from zeep.exceptions import Fault
from zeep.proxy import AsyncOperationProxy, AsyncServiceProxy
from zeep.transports import AsyncTransport
from zeep.wsse import UsernameToken

from combadge.core.binder import BaseBoundService
from combadge.core.container import ServiceContainerMixin
from combadge.core.errors import BackendError
from combadge.core.interfaces import ServiceMethod
from combadge.core.signature import Signature
from combadge.support.soap.request import Request
from combadge.support.zeep.backends.base import BaseZeepBackend, ByBindingName, ByServiceName, MethodMeta


class ZeepBackend(
    BaseZeepBackend[AsyncServiceProxy, AsyncOperationProxy],
    ServiceContainerMixin,
):
    """Asynchronous Zeep service."""

    __slots__ = ("_service", "_service_cache")

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
                address=service.address_string,
            )
        else:
            raise TypeError(type(service))
        return cls(service_proxy)

    def __init__(self, service: AsyncServiceProxy) -> None:
        """
        Instantiate the backend.

        Args:
            service: [service proxy object](https://docs.python-zeep.org/en/master/client.html#the-serviceproxy-object)
        """
        BaseZeepBackend.__init__(self, service)
        ServiceContainerMixin.__init__(self)

    @classmethod
    def bind_method(cls, signature: Signature) -> ServiceMethod[Self]:  # noqa: D102
        meta = cls.inspect(signature)

        async def bound_method(self: BaseBoundService[Self], *args: Any, **kwargs: Any) -> Any:
            request = signature.build_request(Request, self, args, kwargs)
            return await self.__combadge_backend__(request, meta)

        return bound_method  # type: ignore[return-value]

    async def __call__(self, request: Request, meta: MethodMeta) -> Any:  # noqa: D102
        operation = self._get_operation(request.get_operation_name())
        try:
            response = await operation(**(request.payload or {}), _soapheaders=request.soap_header)
        except Fault as e:
            return self._parse_soap_fault(e, meta.fault_type)
        except Exception as e:
            raise BackendError(e) from e
        else:
            return meta.validate_response(response)

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
