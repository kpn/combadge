from __future__ import annotations

from typing import Any, Iterable

from typing_extensions import Annotated, Self, TypeAliasType, get_origin
from typing_extensions import get_args as get_type_args


class AnnotatedMarker:
    """
    Any marker that is supported within an [`Annotated`][1] definition.

    [1]: https://docs.python.org/3/library/typing.html#typing.Annotated
    """

    __slots__ = ()

    @classmethod
    def extract(cls, type_: type[Any] | None) -> Iterable[Self]:
        """Extract all parameter markers from the type annotation, which are instances of the current class."""
        if isinstance(type_, TypeAliasType):
            type_ = type_.__value__
        if get_origin(type_) is Annotated:
            return tuple(arg for arg in get_type_args(type_) if isinstance(arg, cls))
        return ()
