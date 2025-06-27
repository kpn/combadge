"""Internal type variables."""

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from combadge.core.backend import BaseBackend

AnyT = TypeVar("AnyT")

BackendT = TypeVar("BackendT", bound="BaseBackend")
"""Backend type."""

BackendRequestT = TypeVar("BackendRequestT")
"""Backend-specific request type."""

ResponseT = TypeVar("ResponseT")
"""User-defined response type of a service call."""

ServiceProtocolT = TypeVar("ServiceProtocolT")
"""User-defined service protocol type."""

FunctionT = TypeVar("FunctionT", bound=Callable[..., Any])
"""Generic function type without specific purpose."""
