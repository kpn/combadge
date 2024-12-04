from typing import Any

from typing_extensions import TypeAliasType


def drop_type_alias(type_: type[Any] | None) -> type[Any] | None:
    """Extract the inner type, if the given type is an alias."""
    # TODO: tests.
    if isinstance(type_, TypeAliasType):
        type_ = type_.__value__
    return type_
