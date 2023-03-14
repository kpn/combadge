"""Mixins for HTTP-related request classes."""

from abc import ABC
from typing import Any, Dict, List, Optional, Tuple

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


class SupportsJson(ABC, BaseModel):
    """Supports a JSON body."""

    json_: Optional[BaseModel] = None
    """Used with [Json][combadge.support.http.markers.Json]."""

    json_fields: Dict[str, Any] = Field(default_factory=dict)
    """Used with [Json][combadge.support.http.markers.JsonField]."""


class SupportsFormData(ABC, BaseModel):
    """Supports a [form data](https://developer.mozilla.org/en-US/docs/Learn/Forms/Sending_and_retrieving_form_data)."""

    form_data: Optional[BaseModel] = None
    """Used with [Json][combadge.support.http.markers.FormData]."""

    form_fields: Dict[str, List[Any]] = Field(default_factory=dict)
    """Used with [Json][combadge.support.http.markers.FormField]."""

    def append_form_field(self, name: str, value: Any) -> None:  # noqa: D102
        self.form_fields.setdefault(name, []).append(value)
