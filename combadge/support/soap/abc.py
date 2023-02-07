from abc import ABC
from typing import ClassVar

from pydantic import BaseModel, Field
from typing_extensions import Annotated


class RequiresOperationName(ABC, BaseModel):
    """Requires an operation name."""

    KEY: ClassVar[str] = "operation_name"
    operation_name: Annotated[str, Field(..., alias=KEY)]
