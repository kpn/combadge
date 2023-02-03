"""Generic marks applicable to a variety of protocols."""

from typing import Any, Dict, TypeVar

from typing_extensions import Annotated, TypeAlias

from combadge.core.mark import ParameterMark
from combadge.support.abc import RequiresBody


class BodyParameterMark(ParameterMark):
    """Designates a parameter as the service call's request body."""

    def prepare_request(self, request: Dict[str, Any], value: Any) -> None:  # noqa: D102
        request[RequiresBody.KEY] = value


T = TypeVar("T")

_BODY_MARK = BodyParameterMark()
Body: TypeAlias = Annotated[T, _BODY_MARK]
