from __future__ import annotations

from abc import abstractmethod
from typing import Any

from pydantic import BaseModel
from typing_extensions import Protocol, Self

from combadge.core.binder import BaseBoundService, Signature, bind
from combadge.core.typevars import BackendT


class SupportsService(Protocol):
    """
    Convenience protocol that forwards the `bind` call.

    You can still inherit from `Protocol` directly and call `bind` manually.
    """

    @classmethod
    def bind(cls, to_backend: ProvidesBinder) -> Self:
        """Bind the current protocol to the specified backend."""
        return bind(cls, to_backend)


class MethodBinder(Protocol[BackendT]):  # noqa: D101
    @staticmethod
    @abstractmethod
    def __call__(__signature: Signature) -> CallServiceMethod[BackendT]:
        """
        Bind the method by its signature (for example, a backend).

        Args:
            __signature: extracted method signature

        Returns:
            Callable service method which is then fully capable of sending a request and receiving a response
            via a corresponding backend instance.
        """
        raise NotImplementedError


class ProvidesBinder(Protocol):
    """
    Provides a default binder for itself.

    This is a convenience protocol that allows implementing a shortcut `bind` method instead of
    forcing a user to bind the class manually.
    """

    binder: MethodBinder[Self]


class CallServiceMethod(Protocol[BackendT]):
    """
    Bound method call specification.

    Usually implemented by a backend in its `bind_method`.
    """

    @abstractmethod
    def __call__(self, __service: BaseBoundService[BackendT], *__args: Any, **__kwargs: Any) -> BaseModel:
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
