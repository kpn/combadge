"""Internal type variables."""

from typing import Callable, TypeVar

from pydantic import BaseModel
from typing_extensions import TypeAlias

RequestT = TypeVar("RequestT", bound=BaseModel)
ResponseT = TypeVar("ResponseT", bound=BaseModel)
ServiceProtocolT = TypeVar("ServiceProtocolT")

_T = TypeVar("_T")
Identity: TypeAlias = Callable[[_T], _T]
