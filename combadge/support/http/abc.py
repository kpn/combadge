"""Mixins for HTTP-related request classes."""

from abc import ABC
from typing import Any, List, Tuple

from pydantic import BaseModel, Field
from typing_extensions import Annotated


class SupportsHeaders(ABC, BaseModel):
    """Adds support for additional HTTP headers."""

    headers: Annotated[List[Tuple[str, Any]], Field(default_factory=list)]


class RequiresPath(ABC, BaseModel):
    """Requires a request URL path."""

    path: str


class RequiresMethod(ABC, BaseModel):
    """Requires a request HTTP method."""

    method: str


class SupportsQueryParams(ABC, BaseModel):
    """Supports query parameters."""

    query_params: Annotated[List[Tuple[str, Any]], Field(default_factory=list)]
