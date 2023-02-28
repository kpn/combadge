from abc import ABC
from typing import Optional

from pydantic import BaseModel


class SupportsJson(ABC, BaseModel):
    """Supports a JSON body."""

    json_: Optional[BaseModel] = None
