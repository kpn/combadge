"""Internal type variables."""

from typing import Any, Callable, TypeVar, TypedDict

AnyType = TypeVar("AnyType")
"""Generic type variable without any particular constraints."""

BackendT = TypeVar("BackendT", bound="SupportsBackend")
"""Backend type."""

BackendRequestSpecificationT = TypeVar("BackendRequestSpecificationT", bound=TypedDict)
"""
Backend-specific request specification.

It defines which key-value pairs the backend supports when called.
"""

BackendResponseSpecificationT = TypeVar("BackendResponseSpecificationT", bound=TypedDict)
"""
Backend-specific response specification.

It defines which key-value pairs are available in the backend call result.
"""

BackendResponseValidatorT = TypeVar("BackendResponseValidatorT")
"""
Backend-specific response validator.

It must accept a response formed according to the response specification.
"""

ResponseT = TypeVar("ResponseT")
"""User-defined response type of a service call."""

ServiceProtocolT = TypeVar("ServiceProtocolT")
"""User-defined service protocol type."""

FunctionT = TypeVar("FunctionT", bound=Callable[..., Any])
"""Generic function type."""
