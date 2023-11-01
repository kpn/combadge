"""Internal type variables."""

from typing import Any, Callable, TypeVar

BackendT = TypeVar("BackendT")
RequestT = TypeVar("RequestT")
ResponseT = TypeVar("ResponseT")
ServiceProtocolT = TypeVar("ServiceProtocolT")

FunctionT = TypeVar("FunctionT", bound=Callable[..., Any])
