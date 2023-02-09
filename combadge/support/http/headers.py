"""Generic HTTP headers."""

from typing import TypeVar

from typing_extensions import Annotated, TypeAlias

from combadge.support.http.marks import Header

T = TypeVar("T")

AcceptLanguage: TypeAlias = Annotated[T, Header("Accept-Language")]
# TODO: more headers.
# TODO: typed headers?
