from typing import TypeVar

from pydantic import BaseModel

# TODO: move to a more appropriate place.
ResponseT = TypeVar("ResponseT", bound=BaseModel)
ServiceProtocolT = TypeVar("ServiceProtocolT")
