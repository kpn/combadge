from __future__ import annotations

from abc import abstractmethod
from typing import Any, Protocol

from typing_extensions import Self

from combadge.core.binder import BaseBoundService
from combadge.core.signature import Signature
from combadge.core.typevars import BackendRequestSpecificationT, BackendT, BackendResponseSpecificationT, \
    BackendResponseValidatorT


# TODO: possibly, make it an abstract class with included service container.
class SupportsBackend(Protocol[BackendRequestSpecificationT, BackendResponseSpecificationT, BackendResponseValidatorT]):
    """Backend protocol."""

    @classmethod
    @abstractmethod
    def inspect(cls, signature: Signature) -> BackendResponseValidatorT:
        """Extract metadata needed by the backend to execute the specific service method."""
        raise NotImplementedError

    @abstractmethod
    def __call__(self, request: BackendRequestSpecificationT) -> BackendResponseSpecificationT:
        """
        Call the backend.

        Args:
            request: request to be executed by the backend

        Returns:
            Non-validated response. Async backend should naturally return
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
