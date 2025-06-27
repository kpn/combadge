from __future__ import annotations

from itertools import chain
from types import UnionType
from typing import Annotated, Any, Union, get_origin
from typing import get_args as get_type_args

from typing_extensions import Self, TypeAliasType


class AnnotatedMarker:
    """
    Any marker that is supported within an [`Annotated`][1] definition.

    [1]: https://docs.python.org/3/library/typing.html#typing.Annotated
    """

    __slots__ = ()

    @classmethod
    def extract(cls, type_: type[Any] | None) -> list[Self]:
        """Extract all parameter markers from the type annotation, which are instances of the current class."""
        if isinstance(type_, TypeAliasType):
            type_ = type_.__value__
        type_origin = get_origin(type_)
        if type_origin is Annotated:
            return list(
                chain.from_iterable(
                    (arg,)
                    if isinstance(arg, cls)  # it's just a marker then
                    else cls.extract(arg)  # try and extract markers from the type parameter
                    for arg in get_type_args(type_)
                ),
            )
        if type_origin in (Union, UnionType):
            # Extract marker from the union alternatives:
            return [marker for inner_type in get_type_args(type_) for marker in cls.extract(inner_type)]
        return []
