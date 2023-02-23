from typing import TypeVar

from typing_extensions import Annotated, TypeAlias

from combadge.support.http.markers import Header

_T = TypeVar("_T")

AcceptLanguage: TypeAlias = Annotated[_T, Header("Accept-Language")]
# TODO: more headers.
# TODO: typed headers?
