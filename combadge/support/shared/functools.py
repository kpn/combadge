from functools import lru_cache
from typing import Any

from pydantic import TypeAdapter


@lru_cache(maxsize=None)
def get_type_adapter(type_: Any) -> TypeAdapter[Any]:
    """Get cached type adapter for the given type."""
    return TypeAdapter(type_)
