from typing import Any, Dict, Type

from combadge.core.binder import bind
from combadge.core.interfaces import ProvidesBinder
from combadge.core.typevars import ServiceProtocolT


class ServiceContainer(ProvidesBinder):  # noqa: D101
    def __init__(self) -> None:  # noqa: D107
        self._service_cache: Dict[Type, Any] = {}

    def __getitem__(self, protocol: Type[ServiceProtocolT]) -> ServiceProtocolT:
        """
        Bind the protocol to the current backend and return the service instance.

        This method caches the service instances, and so may be used repeatedly
        without a performance impact.

        Examples:
            >>> class ServiceProtocol(Protocol): ...
            >>> service = BackendClass()[ServiceProtocol]
        """
        service = self._service_cache.get(protocol)
        if service is None:
            service = self._service_cache[protocol] = bind(protocol, self)
        return service  # noqa: RET504

    def __delitem__(self, protocol: Type) -> None:
        """
        Delete the cached service instance for the specified protocol.

        Tip: This operation is idempotent
            It is safe to remove a non-existing service instance.
        """
        self._service_cache.pop(protocol)
