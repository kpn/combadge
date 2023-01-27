from __future__ import annotations

from abc import abstractmethod
from typing import Any, Awaitable, TypeVar, Union

from pydantic import BaseModel
from typing_extensions import Protocol, Self

from combadge.binder import BaseBoundService, bind
from combadge.response import ResponseT, ResponseT_co


class SupportsService(Protocol):
    """
    Convenience protocol that forwards the `bind` call.

    You can still inherit from `Protocol` directly and call `bind` manually.
    """

    @classmethod
    def bind(cls, to_backend: SupportsBindMethod) -> Self:
        """Bind the protocol to the specified backend."""
        return bind(cls, to_backend)


ServiceProtocolT = TypeVar("ServiceProtocolT")

RequestT = TypeVar("RequestT", bound=BaseModel)
RequestT_contra = TypeVar("RequestT_contra", bound=BaseModel, contravariant=True)


class SupportsBindMethod(Protocol):
    """Supports binding a method to the current instance."""

    @abstractmethod
    def bind_method(
        self,
        request_type: type[RequestT],
        response_type: type[ResponseT],
        method: Any,
    ) -> SupportsMethodCall[RequestT, ResponseT]:
        """
        «Binds» the `method` to the current instance (for example, a backend).

        Args:
            request_type: request type extracted from the service protocol
            response_type: response type extracted from the service protocol
            method: original protocol method

        Returns:
            Callable service method which is fully capable of sending a request and receiving a response.
        """
        raise NotImplementedError


class SupportsMethodCall(Protocol[RequestT_contra, ResponseT_co]):
    """Bound method call specification. Usually implemented by a backend in its `bind_method`."""

    @abstractmethod
    def __call__(
        self,
        __service: BaseBoundService,
        __request: RequestT_contra,
    ) -> Union[ResponseT_co, Awaitable[ResponseT_co]]:
        """
        Call the service method.

        Args:
            __service: bound service instance, usually not needed
            __request: request model

        Returns:
            Parsed response model.
        """
        raise NotImplementedError
