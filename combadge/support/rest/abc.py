from abc import ABC
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SupportsJson(ABC, BaseModel):
    """Supports a JSON body."""

    json_: Optional[BaseModel] = None
    """Used with [Json][combadge.support.rest.markers.Json]."""

    json_fields: Dict[str, Any] = Field(default_factory=dict)
    """Used with [Json][combadge.support.rest.markers.JsonField]."""


class SupportsFormData(ABC, BaseModel):
    """Supports a [form data](https://developer.mozilla.org/en-US/docs/Learn/Forms/Sending_and_retrieving_form_data)."""

    form_data: Optional[BaseModel] = None
    """Used with [Json][combadge.support.rest.markers.FormData]."""

    form_fields: Dict[str, List[Any]] = Field(default_factory=dict)
    """Used with [Json][combadge.support.rest.markers.FormField]."""

    def append_form_field(self, name: str, value: Any) -> None:  # noqa: D102
        self.form_fields.setdefault(name, []).append(value)
