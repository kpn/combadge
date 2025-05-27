from typing import Annotated, Any

from typing_extensions import TypeAliasType, get_args, get_origin


try:
    from types import UnionType  # type: ignore[attr-defined]
except ImportError:
    # Before Python 3.10:
    from typing import Union

    UnionType = type(Union[int, str])  # type: ignore[assignment, misc]


def unwrap_type_alias(type_: Any) -> Any:
    """Extract the inner type, if the given type is a type alias."""
    if isinstance(type_, TypeAliasType):
        type_ = type_.__value__
    return type_


def unwrap_annotated(type_: Any) -> Any:
    """Extract the inner type, if the given type is an `Annotated` form."""
    if get_origin(type_) is Annotated:
        type_ = get_args(type_)[0]
    return type_
