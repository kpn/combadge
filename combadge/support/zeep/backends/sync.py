from __future__ import annotations

from collections.abc import Collection
from os import PathLike, fspath
from types import TracebackType
from typing import Any

from typing_extensions import Self
from zeep import Client, Plugin, Transport
from zeep.exceptions import Fault
from zeep.proxy import OperationProxy, ServiceProxy
from zeep.wsse import UsernameToken

from combadge.core.binder import BaseBoundService
from combadge.core.container import ServiceContainerMixin
from combadge.core.errors import BackendError
from combadge.core.interfaces import ServiceMethod
from combadge.core.signature import Signature
from combadge.support.soap.request import Request
from combadge.support.zeep.backends.base import BaseZeepBackend, ByBindingName, ByServiceName, MethodMeta


class ZeepBackend(BaseZeepBackend[ServiceProxy, OperationProxy], ServiceContainerMixin):
    """Synchronous Zeep service."""

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
        verify_ssl: bool | PathLike = True,
        cert_file: PathLike | None = None,
        key_file: PathLike | None = None,
    ) -> ZeepBackend:
        """
        Instantiate the backend using a set of the most common parameters.

        Using the `__init__()` may become quite wordy, so this method simplifies typical use cases.
        """
        client = Client(
            fspath(wsdl_path),
            wsse=wsse,
            transport=Transport(timeout=load_timeout, operation_timeout=operation_timeout),
            plugins=plugins,
        )
        client.transport.session.verify = verify_ssl if isinstance(verify_ssl, bool) else fspath(verify_ssl)
        client.transport.session.cert = (
            fspath(cert_file) if cert_file is not None else None,
            fspath(key_file) if key_file is not None else None,
        )
        if service is None:
            service_proxy = client.service
        elif isinstance(service, ByServiceName):
            service_proxy = client.bind(service.service_name, service.port_name)
        elif isinstance(service, ByBindingName):
            service_proxy = client.create_service(service.binding_name, service.address_string)
        else:
            raise TypeError(type(service))
        return cls(service_proxy)

    def __init__(
        self,
        service: ServiceProxy,
    ) -> None:
        """
        Instantiate the backend.

        Args:
            service: [service proxy object](https://docs.python-zeep.org/en/master/client.html#the-serviceproxy-object)
        """
        BaseZeepBackend.__init__(self, service)
        ServiceContainerMixin.__init__(self)

    def bind_method(self, signature: Signature) -> ServiceMethod[Self]:  # noqa: D102
        meta = self.inspect(signature)

        def bound_method(self: BaseBoundService[Self], *args: Any, **kwargs: Any) -> Any:
            request = signature.build_request(Request, self, args, kwargs)
            return self.__combadge_backend__(request, meta)

        return bound_method  # type: ignore[return-value]

    def __call__(self, request: Request, meta: MethodMeta) -> Any:  # noqa: D102
        operation = self._get_operation(request.get_operation_name())
        try:
            response = operation(**(request.payload or {}), _soapheaders=request.soap_header)
        except Fault as e:
            return self._parse_soap_fault(e, meta.fault_type)
        except Exception as e:
            raise BackendError(e) from e
        else:
            return meta.validate_response(response)

    def __enter__(self) -> Self:
        self._service = self._service.__enter__()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> Any:
        return self._service.__exit__(exc_type, exc_value, traceback)
