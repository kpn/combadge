"""Internal type variables."""

from typing import TypeVar

from pydantic import BaseModel

RequestT = TypeVar("RequestT", bound=BaseModel)
ResponseT = TypeVar("ResponseT", bound=BaseModel)
ServiceProtocolT = TypeVar("ServiceProtocolT")
