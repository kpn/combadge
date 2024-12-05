from __future__ import annotations

from abc import abstractmethod
from typing import Any, Protocol

from typing_extensions import Self

from combadge.core.binder import BaseBoundService
from combadge.core.signature import Signature
from combadge.core.typevars import BackendMethodMetaT, BackendRequestT, BackendT


# TODO: possibly, make it an abstract class with included service container.
class SupportsBackend(Protocol[BackendRequestT, BackendMethodMetaT]):
    """Backend protocol."""

    REQUEST_TYPE: type[BackendRequestT]

    @classmethod
    @abstractmethod
    def inspect(cls, signature: Signature) -> BackendMethodMetaT:
        """Extract metadata needed by the backend to execute the specific service method."""
        raise NotImplementedError

    @abstractmethod
    def bind_method(self, signature: Signature, /) -> ServiceMethod[Self]:
        """
        Bind the method by its signature (for example, a backend).

        Args:
            signature: extracted method signature

        Returns:
            Callable service method which is then fully capable of sending a request and receiving a response
            via a corresponding backend instance.
        """
        raise NotImplementedError

    @abstractmethod
    def __call__(self, request: BackendRequestT, meta: BackendMethodMetaT) -> Any:
        """
        Call the backend.

        Args:
            request: request to be executed by the backend
            meta: metadata attached to the service method

        Returns:
            Validated response. Async backend should return
            an [awaitable object](https://docs.python.org/3/library/asyncio-task.html#awaitables).
        """
        raise NotImplementedError


class ServiceMethod(Protocol[BackendT]):
    """
    Bound method call specification.

    Usually implemented by a backend in its `bind_method`.
    """

    @abstractmethod
    def __call__(self, service: BaseBoundService[BackendT], /, *args: Any, **kwargs: Any) -> Any:
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
