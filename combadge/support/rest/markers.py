from dataclasses import dataclass
from typing import Any, TypeVar

from typing_extensions import Annotated, TypeAlias

from combadge.core.markers import ParameterMarker
from combadge.support.rest.abc import SupportsJson

_T = TypeVar("_T")


@dataclass
class JsonParameterMarker(ParameterMarker[SupportsJson]):
    """
    Mark a parameter as a request JSON body.

    Used for a more complex annotations, for example:

    ```python
    Annotated[BodyModel, JsonParameterMarker(), AnotherMarker]
    ```

    For simple annotations prefer the [Body][combadge.support.rest.markers.Json] marker.
    """

    __slots__ = ()

    def prepare_request(self, request: SupportsJson, value: Any) -> None:  # noqa: D102
        request.json_ = value


Json: TypeAlias = Annotated[_T, JsonParameterMarker()]
"""
Mark parameter as a request JSON body. An argument gets converted to a dictionary and passed over to a backend.

Examples:
    >>> from combadge.support.http import Body
    >>>
    >>> class BodyModel(BaseModel):
    >>>     ...
    >>>
    >>> def call(body: Json[BodyModel]) -> ...:
    >>>     ...
"""
