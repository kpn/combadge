from __future__ import annotations

from abc import abstractmethod
from platform import python_implementation
from typing import TypeVar

from pydantic import BaseModel
from typing_extensions import ParamSpec, Protocol, Self

from combadge.core.binder import BaseBoundService, bind
from combadge.core.response import ResponseT, ResponseT_co


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

if python_implementation() != "PyPy":
    RequestP = ParamSpec("RequestP")
else:  # pragma: no cover
    # PyPy doesn't support `ParamSpec` in `Protocol` 😮
    RequestP = TypeVar("RequestP")  # type: ignore[misc]


class SupportsBindMethod(Protocol):
    """Supports binding a method to the current instance."""

    @abstractmethod
    def bind_method(
        self,
        response_type: type[ResponseT],
        method: SupportsMethodCall[RequestP, ResponseT],
    ) -> SupportsMethodCall[RequestP, ResponseT]:
        """
        «Binds» the `method` to the current instance (for example, a backend).

        Args:
            response_type: response type extracted from the service protocol
            method: original protocol method

        Returns:
            Callable service method which is fully capable of sending a request and receiving a response.
        """
        raise NotImplementedError


class SupportsMethodCall(Protocol[RequestP, ResponseT_co]):
    """
    Bound method call specification.

    Usually implemented by a backend in its `bind_method`.
    """

    @abstractmethod
    def __call__(
        self,
        __service: BaseBoundService,
        *__args: RequestP.args,
        **__kwargs: RequestP.kwargs,
    ) -> ResponseT_co:
        """
        Call the service method.

        Args:
            __service: bound service instance, usually not needed
            __args: positional request parameters
            __kwargs: keyword request parameters

        Returns:
            Parsed response model.
        """
        raise NotImplementedError
