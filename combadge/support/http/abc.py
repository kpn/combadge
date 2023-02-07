"""Protocol-specific abstract base classes."""

from abc import ABC
from typing import Any, ClassVar, List, Tuple

from pydantic import BaseModel, Field
from typing_extensions import Annotated


class RequiresBody(ABC, BaseModel):
    """Requires a request body (for example, a JSON payload or a SOAP body)."""

    KEY: ClassVar[str] = "body"
    body: Annotated[BaseModel, Field(..., alias=KEY)]


class SupportsHeaders(ABC, BaseModel):
    """Adds support for additional HTTP headers."""

    KEY: ClassVar[str] = "headers"
    headers: Annotated[List[Tuple[str, Any]], Field(alias=KEY, default_factory=list)]


class RequiresPath(ABC, BaseModel):
    """Requires a request URL path."""

    KEY: ClassVar[str] = "path"
    path: Annotated[str, Field(..., alias=KEY)]
