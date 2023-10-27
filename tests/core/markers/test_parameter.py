from typing import Any, List, Type

import pytest
from typing_extensions import Annotated

from combadge.core.markers.parameter import ParameterMarker
from combadge.support.http.markers import CustomHeader
from combadge.support.http.markers.implementation import CustomHeader as CustomHeaderImplementation
from combadge.support.soap.markers import Body
from combadge.support.soap.markers.implementation import Body as BodyImplementation


@pytest.mark.parametrize(
    ("type_", "expected"),
    [
        (int, []),
        (Body[int], [BodyImplementation()]),
        (Annotated[str, CustomHeader("X-Header")], [CustomHeaderImplementation("X-Header")]),
    ],
)
def test_extract_parameter_marks(type_: Type[Any], expected: List[ParameterMarker]) -> None:
    assert ParameterMarker.extract(type_) == expected
