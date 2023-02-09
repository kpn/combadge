"""These are building blocks (à la mixins) of concrete backend's request classes."""

from abc import ABC
from typing import Any, ClassVar, List, Tuple

from pydantic import BaseModel, Field
from typing_extensions import Annotated


class RequiresPath(ABC, BaseModel):
    """Requires a request URL path."""

    KEY: ClassVar[str] = "path"
    path: Annotated[str, Field(..., alias=KEY)]


class RequiresMethod(ABC, BaseModel):
    """Requires a request method (for example, HTTP method)."""

    KEY: ClassVar[str] = "method"
    method: Annotated[str, Field(..., alias=KEY)]


class SupportsQueryParams(ABC, BaseModel):
    """Supports query parameters."""

    KEY: ClassVar[str] = "query_params"
    query_params: Annotated[List[Tuple[str, Any]], Field(default_factory=list)]
