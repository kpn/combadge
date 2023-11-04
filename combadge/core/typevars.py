"""Internal type variables."""

from typing import Any, Callable, TypeVar

BackendT = TypeVar("BackendT")
"""Backend type."""

BackendRequestT = TypeVar("BackendRequestT")
"""Backend-specific request type."""

BackendResponseT = TypeVar("BackendResponseT")
"""Backend-specific response type."""

ResponseT = TypeVar("ResponseT")
"""User-defined response type of a service call."""

ServiceProtocolT = TypeVar("ServiceProtocolT")
"""User-defined service protocol type."""

FunctionT = TypeVar("FunctionT", bound=Callable[..., Any])
"""Generic function type without specific purpose."""
