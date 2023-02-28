from abc import ABC
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class SupportsJson(ABC, BaseModel):
    """Supports a JSON body."""

    json_: Optional[BaseModel] = None
    """Used with [Json][combadge.support.rest.markers.Json]."""

    json_fields: Dict[str, Any] = Field(default_factory=dict)
    """Used with [Json][combadge.support.rest.markers.JsonField]."""
