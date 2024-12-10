from __future__ import annotations

from collections.abc import Iterable
from typing import Annotated, Any

from typing_extensions import Self, get_origin
from typing_extensions import get_args as get_type_args

from combadge._helpers.typing import unwrap_type_alias


class AnnotatedMarker:
    """
    Any marker that is supported within an [`Annotated`][1] definition.

    [1]: https://docs.python.org/3/library/typing.html#typing.Annotated
    """

    __slots__ = ()

    @classmethod
    def extract(cls, type_: type[Any] | None) -> Iterable[Self]:
        """Extract all parameter markers from the type annotation, which are instances of the current class."""
        type_ = unwrap_type_alias(type_)
        if get_origin(type_) is Annotated:
            return tuple(arg for arg in get_type_args(type_) if isinstance(arg, cls))
        return ()
