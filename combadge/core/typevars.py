"""Internal type variables."""

from typing import TYPE_CHECKING, Any, Callable, TypeVar

if TYPE_CHECKING:
    from combadge.core.interfaces import SupportsBackend

AnyType = TypeVar("AnyType")
"""Generic type variable without any particular constraints."""

BackendT = TypeVar("BackendT", bound="SupportsBackend")
"""Backend type."""

BackendMethodMetaT = TypeVar("BackendMethodMetaT")
"""Backend-specific metadata attached to a service method."""

BackendRequestT = TypeVar("BackendRequestT")
"""Backend-specific request type."""

ResponseT = TypeVar("ResponseT")
"""User-defined response type of a service call."""

ServiceProtocolT = TypeVar("ServiceProtocolT")
"""User-defined service protocol type."""

FunctionT = TypeVar("FunctionT", bound=Callable[..., Any])
"""Generic function type."""
