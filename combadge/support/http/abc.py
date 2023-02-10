"""Mixins for HTTP-related request classes."""

from abc import ABC
from typing import Any, List, Optional, Tuple

from pydantic import BaseModel, Field
from typing_extensions import Annotated


class SupportsHeaders(ABC, BaseModel):
    """Adds support for additional HTTP headers."""

    headers: Annotated[List[Tuple[str, Any]], Field(default_factory=list)]


class RequiresBody(ABC, BaseModel):
    """Requires a request body (for example, a JSON payload or a SOAP body)."""

    body: BaseModel


class SupportsBody(ABC, BaseModel):
    """Supports an optional request body (for example, a JSON payload or a SOAP body)."""

    body: Optional[BaseModel] = None
