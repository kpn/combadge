from abc import ABC, abstractmethod
from typing import Any

from typing_extensions import Self

from combadge.core.binder import bind
from combadge.core.interfaces import ServiceMethod
from combadge.core.signature import Signature
from combadge.core.typevars import ServiceProtocolT


class BaseBackend(ABC):
    """
    Abstract base backend class.

    - It provides an entry point for binding a service method to the backend.
    - It also caches all the service instances bound to the backend via the item protocol.
    """

    __slots__ = ("_service_cache",)

    def __init__(self) -> None:  # noqa: D107
        self._service_cache: dict[type, Any] = {}

    @classmethod
    @abstractmethod
    def bind_method(cls, signature: Signature, /) -> ServiceMethod[Self]:
        """
        Bind the method by its signature.

        Args:
            signature: extracted method signature

        Returns:
            Callable service method which is fully capable of sending a request and receiving a response
            via this backend.
        """
        raise NotImplementedError

    def __getitem__(self, protocol: type[ServiceProtocolT]) -> ServiceProtocolT:
        """
        Bind the given protocol to this backend and return the bound service instance.

        This method caches the service instances, and so may be used repeatedly
        without a huge performance impact.

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
            service = self._service_cache[protocol] = bind(protocol, self)
        return service  # noqa: RET504

    def __delitem__(self, protocol: type) -> None:
        """
        Delete the cached service instance for the specified protocol.

        Tip: This operation is idempotent
            It is safe to remove a non-existing service instance.
        """
        self._service_cache.pop(protocol)
