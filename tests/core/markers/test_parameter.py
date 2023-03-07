from typing import Any, List, Type

import pytest
from typing_extensions import Annotated

from combadge.core.markers.parameter import ParameterMarker
from combadge.support.http.headers import AcceptLanguage
from combadge.support.http.markers import Header, HeaderParameterMarker
from combadge.support.soap.markers import Body, BodyParameterMarker


@pytest.mark.parametrize(
    ("type_", "expected"),
    [
        (int, []),
        (Body[int], [BodyParameterMarker()]),
        (Annotated[str, Header("X-Header")], [HeaderParameterMarker("X-Header")]),
        (AcceptLanguage[str], [HeaderParameterMarker("Accept-Language")]),
    ],
)
def test_extract_parameter_marks(type_: Type[Any], expected: List[ParameterMarker]) -> None:
    assert ParameterMarker.extract(type_) == expected
