"""Protocol-specific abstract base classes."""

from abc import ABC
from typing import ClassVar

from pydantic import BaseModel, Field
from typing_extensions import Annotated


class RequiresOperationName(ABC, BaseModel):
    """Adds support of an operation name (for example, a SOAP name)."""

    KEY: ClassVar[str] = "operation_name"
    operation_name: Annotated[str, Field(..., alias=KEY)]


class RequiresBody(ABC, BaseModel):
    """Add support of a body (for example, a JSON payload or a SOAP body)."""

    KEY: ClassVar[str] = "body"
    body: Annotated[BaseModel, Field(..., alias=KEY)]
