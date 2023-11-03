"""Internal type variables."""

from typing import Any, Callable, TypeVar

BackendT = TypeVar("BackendT")
"""Backend type."""

RequestT = TypeVar("RequestT")
"""Backend-specific request type."""

ResponseT = TypeVar("ResponseT")
"""Final response type of a service call."""

ServiceProtocolT = TypeVar("ServiceProtocolT")
"""User service protocol type."""

FunctionT = TypeVar("FunctionT", bound=Callable[..., Any])
"""Generic function type without specific purpose."""
