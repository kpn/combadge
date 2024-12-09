from typing import Annotated, Any

import pytest

from combadge.core.markers.parameter import ParameterMarker
from combadge.support.http.request import CustomHeader


@pytest.mark.parametrize(
    ("type_", "expected"),
    [
        (int, []),
        (Annotated[str, CustomHeader("X-Header")], [CustomHeader("X-Header")]),
    ],
)
def test_extract_parameter_marks(type_: type[Any], expected: list[ParameterMarker]) -> None:
    assert list(ParameterMarker.extract(type_)) == expected
