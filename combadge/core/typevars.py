from typing import TypeVar

from pydantic import BaseModel

ResponseT = TypeVar("ResponseT", bound=BaseModel)
ServiceProtocolT = TypeVar("ServiceProtocolT")
