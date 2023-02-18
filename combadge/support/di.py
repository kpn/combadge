"""Dependency injection support."""

from typing import Any, Callable, Dict, Type

from combadge.core.typevars import ServiceProtocolT


class _ServiceContainer:
    __slots__ = ("_factories",)

    def __init__(self) -> None:
        self._factories: Dict[Type, Callable[[], Any]] = {}

    def register_singleton(self, protocol_type: Type[ServiceProtocolT], service_instance: ServiceProtocolT) -> None:
        """Register the service instance."""
        self.register_factory(protocol_type, lambda: service_instance)

    def __setitem__(self, protocol_type: Type[ServiceProtocolT], service_instance: ServiceProtocolT) -> None:
        """Register the service instance (shorthand for `register_singleton`)."""
        self.register_singleton(protocol_type, service_instance)

    def register_factory(
        self,
        protocol_type: Type[ServiceProtocolT],
        instance_factory: Callable[[], ServiceProtocolT],
    ) -> None:
        """
        Register the instance factory for the specified protocol type.

        It's the lowest-level API. Please, consider using `register_singleton()` instead.
        This method is particularly harmful, if you're passing a heavy factory
        (for example, if the factory instantiates a service on each factory's call).

        The reason for this method to exist is to keep the service container extendable
        (for example, to allow for thread-local service instances).
        """
        self._factories[protocol_type] = instance_factory

    def __getitem__(self, protocol_type: Type[ServiceProtocolT]) -> ServiceProtocolT:
        """Get a service instance for the specified service protocol type."""
        try:
            factory = self._factories[protocol_type]
        except KeyError as e:
            raise KeyError(f"protocol type `{protocol_type}` is not registered") from e
        else:
            return factory()


services = _ServiceContainer()
"""Manages service protocols."""
