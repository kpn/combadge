from __future__ import annotations

from contextlib import AbstractContextManager, nullcontext
from os import PathLike, fspath
from types import TracebackType
from typing import Any, Callable, Collection

from typing_extensions import Self
from zeep import Client, Plugin, Transport
from zeep.exceptions import Fault
from zeep.helpers import serialize_object
from zeep.proxy import OperationProxy, ServiceProxy
from zeep.wsse import UsernameToken

from combadge.core.backend import ServiceContainer
from combadge.core.binder import BaseBoundService
from combadge.core.interfaces import ServiceMethod
from combadge.core.signature import Signature
from combadge.support.shared.sync import SupportsRequestWith
from combadge.support.soap.request import Request
from combadge.support.zeep.backends.base import BaseZeepBackend, ByBindingName, ByServiceName


class ZeepBackend(BaseZeepBackend[ServiceProxy, OperationProxy], SupportsRequestWith[Request], ServiceContainer):
    """Synchronous Zeep service."""

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
            service_proxy = client.create_service(service.binding_name, service.address)
        else:
            raise TypeError(type(service))
        return cls(service_proxy)

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

    def bind_method(self, signature: Signature) -> ServiceMethod[ZeepBackend]:  # noqa: D102
        response_type, fault_type = self._adapt_response_type(signature.return_type)
        backend = self

        def bound_method(self: BaseBoundService[ZeepBackend], *args: Any, **kwargs: Any) -> Any:
            request = signature.build_request(Request, self, args, kwargs)
            operation = backend._get_operation(request.get_operation_name())
            try:
                with self.backend._request_with(request):
                    response = operation(**(request.payload or {}))
            except Fault as e:
                return backend._parse_soap_fault(e, fault_type)
            else:
                return signature.apply_response_markers(response, serialize_object(response, dict), response_type)

        return bound_method  # type: ignore[return-value]

    binder = bind_method  # type: ignore[assignment]

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
