from typing import Annotated, Any

from typing_extensions import TypeAliasType, get_args, get_origin


def drop_type_alias(type_: type[Any] | None) -> type[Any] | None:
    """Extract the inner type, if the given type is an alias."""
    # TODO: tests.
    if isinstance(type_, TypeAliasType):
        type_ = type_.__value__
    return type_


def drop_annotated(type_: type[Any] | None) -> type[Any] | None:
    """Extract the inner type, if the given type is `Annotated`."""
    # TODO: tests.
    if get_origin(type_) is Annotated:
        type_ = get_args(type_)[0]
    return type_
