from __future__ import annotations

from abc import abstractmethod
from typing import Any

from pydantic import BaseModel
from typing_extensions import Protocol, Self

from combadge.core.binder import BaseBoundService, bind


class SupportsService(Protocol):
    """
    Convenience protocol that forwards the `bind` call.

    You can still inherit from `Protocol` directly and call `bind` manually.
    """

    @classmethod
    def bind(cls, to_backend: SupportsBindMethod) -> Self:
        """Bind the protocol to the specified backend."""
        return bind(cls, to_backend)


class SupportsBindMethod(Protocol):
    """Supports binding a method to the current instance."""

    @abstractmethod
    def bind_method(self, response_type: type[BaseModel], method: SupportsMethodCall) -> SupportsMethodCall:
        """
        «Binds» the `method` to the current instance (for example, a backend).

        Args:
            response_type: response type extracted from the service protocol
            method: original protocol method

        Returns:
            Callable service method which is fully capable of sending a request and receiving a response.
        """
        raise NotImplementedError


class SupportsMethodCall(Protocol):
    """
    Bound method call specification.

    Usually implemented by a backend in its `bind_method`.
    """

    @abstractmethod
    def __call__(self, __service: BaseBoundService, *__args: Any, **__kwargs: Any) -> BaseModel:
        """
        Call the service method.

        Args:
            __service: bound service instance
            __args: positional request parameters
            __kwargs: keyword request parameters

        Returns:
            Parsed response model.
        """
        raise NotImplementedError
