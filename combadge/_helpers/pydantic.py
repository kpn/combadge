from functools import cache

from pydantic import TypeAdapter
from typing_extensions import TypeForm

from combadge.core.typevars import AnyT


@cache
def get_type_adapter(type_: TypeForm[AnyT]) -> TypeAdapter[AnyT]:
    """Get cached type adapter for the given type."""
    return TypeAdapter(type_)
