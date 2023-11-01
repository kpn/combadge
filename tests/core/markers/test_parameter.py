from typing import Any, List, Type

import pytest
from typing_extensions import Annotated

from combadge.core.markers.parameter import ParameterMarker
from combadge.support.http.markers import CustomHeader
from combadge.support.http.markers import Payload as PayloadImplementation
from combadge.support.http.markers.shortcuts import Payload


@pytest.mark.parametrize(
    ("type_", "expected"),
    [
        (int, []),
        (Payload[int], [PayloadImplementation()]),
        (Annotated[str, CustomHeader("X-Header")], [CustomHeader("X-Header")]),
    ],
)
def test_extract_parameter_marks(type_: Type[Any], expected: List[ParameterMarker]) -> None:
    assert ParameterMarker.extract(type_) == expected
