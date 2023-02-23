from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Type

from typing_extensions import Annotated, get_args, get_origin


@dataclass(frozen=True)
class ResponseMarker:
    """
    Used to mark response attributes.

    Unlike method and parameters marks, response marks cannot be implemented in a generic way.
    Thus, they're singletons checked by specific backend implementations.
    Backend MAY NOT implement all the predefined response marks,
    and if a particular mark is not supported, the backend MUST issue a warning.
    """

    name: str
    __slots__ = ("name",)

    @classmethod
    def extract(cls, from_type: Type[Any]) -> List[ResponseMarker]:
        """Extract all response markers from the attribute type annotation."""
        if get_origin(from_type) is Annotated:
            return [arg for arg in get_args(from_type) if isinstance(arg, cls)]
        return []
