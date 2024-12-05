"""
In Combadge, all backends implement sort of a _service container_:
the backend caches all service instances that have been bound to the backend.

That makes binding as simple as:

```python
my_service = my_backend[MyServiceProtocol]
```
"""  # noqa: D205

from abc import ABCMeta
from typing import Any

from combadge.core.binder import bind_class
from combadge.core.interfaces import SupportsBackend
from combadge.core.typevars import ServiceProtocolT


class ServiceContainerMixin(SupportsBackend, metaclass=ABCMeta):
    """Service container implementation for backend classes."""

    def __init__(self) -> None:  # noqa: D107
        self._service_cache: dict[type, Any] = {}

    def __getitem__(self, protocol: type[ServiceProtocolT]) -> ServiceProtocolT:
        """
        Bind the protocol to the current backend and return the service instance.

        This method caches the service instances, and so may be used repeatedly
        without a performance impact.

        Examples:
            >>> class ServiceProtocolA(Protocol): ...
            >>> class ServiceProtocolB(Protocol): ...
            >>>
            >>> backend = HttpxBackend()
            >>>
            >>> service_a = backend[ServiceProtocolA]
            >>> service_b = backend[ServiceProtocolB]
        """
        service = self._service_cache.get(protocol)
        if service is None:
            service = self._service_cache[protocol] = bind_class(protocol, type(self))(self)
        return service  # noqa: RET504

    def __delitem__(self, protocol: type) -> None:
        """
        Delete the cached service instance for the specified protocol.

        Tip: This operation is idempotent
            It is safe to remove a non-existing service instance.
        """
        self._service_cache.pop(protocol)
