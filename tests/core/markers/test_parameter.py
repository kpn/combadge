from typing import Any, List, Type

import pytest
from typing_extensions import Annotated

from combadge.core.markers.parameter import ParameterMarker
from combadge.support.http.markers import CustomHeader, CustomHeaderMarker
from combadge.support.soap.markers import Body, BodyMarker


@pytest.mark.parametrize(
    ("type_", "expected"),
    [
        (int, []),
        (Body[int], [BodyMarker()]),
        (Annotated[str, CustomHeader("X-Header")], [CustomHeaderMarker("X-Header")]),
    ],
)
def test_extract_parameter_marks(type_: Type[Any], expected: List[ParameterMarker]) -> None:
    assert ParameterMarker.extract(type_) == expected
