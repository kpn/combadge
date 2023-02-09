from dataclasses import dataclass
from typing import Any, Dict, TypeVar

from typing_extensions import Annotated, TypeAlias

from combadge.core.mark import ParameterMark
from combadge.support.http.abc import RequiresBody, SupportsHeaders

T = TypeVar("T")


@dataclass
class BodyParameterMark(ParameterMark):
    """Designates a parameter a service call's request body."""

    __slots__ = ()

    def prepare_request(self, request: Dict[str, Any], value: Any) -> None:  # noqa: D102
        request[RequiresBody.KEY] = value


Body: TypeAlias = Annotated[T, BodyParameterMark()]


@dataclass
class HeaderParameterMark(ParameterMark):
    """Designates parameter as a service call's additional header."""

    name: str
    __slots__ = ("name",)

    def prepare_request(self, request: Dict[str, Any], value: Any) -> None:  # noqa: D102
        request.setdefault(SupportsHeaders.KEY, []).append((self.name, value))


Header: TypeAlias = HeaderParameterMark
