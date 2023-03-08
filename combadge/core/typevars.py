"""Internal type variables."""

from typing import Any, Callable, TypeVar

from pydantic import BaseModel

BackendT = TypeVar("BackendT")
RequestT = TypeVar("RequestT", bound=BaseModel)
ResponseT = TypeVar("ResponseT", bound=BaseModel)
ServiceProtocolT = TypeVar("ServiceProtocolT")

FunctionT = TypeVar("FunctionT", bound=Callable[..., Any])
