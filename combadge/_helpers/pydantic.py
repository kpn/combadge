from functools import cache

from pydantic import TypeAdapter

from combadge.core.typevars import AnyT


@cache
def get_type_adapter(type_: AnyT) -> TypeAdapter[AnyT]:
    """Get cached type adapter for the given type."""
    return TypeAdapter(type_)
