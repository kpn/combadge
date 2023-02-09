from abc import ABC
from typing import Any, ClassVar, List, Optional, Tuple

from pydantic import BaseModel, Field
from typing_extensions import Annotated


class SupportsHeaders(ABC, BaseModel):
    """Adds support for additional HTTP headers."""

    KEY: ClassVar[str] = "headers"
    headers: Annotated[List[Tuple[str, Any]], Field(alias=KEY, default_factory=list)]


class RequiresBody(ABC, BaseModel):
    """Requires a request body (for example, a JSON payload or a SOAP body)."""

    KEY: ClassVar[str] = "body"
    body: Annotated[BaseModel, Field(..., alias=KEY)]


class SupportsBody(ABC, BaseModel):
    """Supports an optional request body (for example, a JSON payload or a SOAP body)."""

    KEY: ClassVar[str] = "body"
    body: Annotated[Optional[BaseModel], Field(alias=KEY)] = None
