from __future__ import annotations

from abc import abstractmethod
from types import TracebackType
from typing import Any, Protocol

from pydantic import BaseModel
from typing_extensions import Self

from combadge.core.binder import BaseBoundService, bind
from combadge.core.signature import Signature
from combadge.core.typevars import BackendT


class SupportsService(Protocol):
    """
    Convenience base for service protocols.

    Tip:
        Combadge can inspect any `Protocol` or `ABC`.
        But it might be a little easier to inherit from `#!python SupportsService`
        since it provides the `bind(to_backend)` method as a shorthand for `#!python bind(from_protocol, to_backend)`.
    """

    @classmethod
    def bind(cls, to_backend: ProvidesBinder, /) -> Self:
        """Bind the current protocol to the specified backend."""
        return bind(cls, to_backend)

    def __enter__(self) -> Self:
        return self

    async def __aenter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> Any:
        return None

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> Any:
        return None


class MethodBinder(Protocol[BackendT]):  # noqa: D101
    @staticmethod
    @abstractmethod
    def __call__(signature: Signature, /) -> ServiceMethod[BackendT]:
        """
        Bind the method by its signature (for example, a backend).

        Args:
            signature: extracted method signature

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


class ServiceMethod(Protocol[BackendT]):
    """
    Bound method call specification.

    Usually implemented by a backend in its `bind_method`.
    """

    @abstractmethod
    def __call__(self, service: BaseBoundService[BackendT], /, *args: Any, **kwargs: Any) -> BaseModel:
        """
        Call the service method.

        Args:
            service: bound service instance
            args: positional request parameters
            kwargs: keyword request parameters

        Returns:
            Parsed response model.
        """
        raise NotImplementedError
