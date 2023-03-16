from typing import Any, List, Type

import pytest
from typing_extensions import Annotated

from combadge.core.markers.parameter import ParameterMarker
from combadge.support.http.headers import AcceptLanguage
from combadge.support.http.markers import Header, HeaderMarker
from combadge.support.soap.markers import Body, BodyMarker


@pytest.mark.parametrize(
    ("type_", "expected"),
    [
        (int, []),
        (Body[int], [BodyMarker()]),
        (Annotated[str, Header("X-Header")], [HeaderMarker("X-Header")]),
        (AcceptLanguage[str], [HeaderMarker("Accept-Language")]),
    ],
)
def test_extract_parameter_marks(type_: Type[Any], expected: List[ParameterMarker]) -> None:
    assert ParameterMarker.extract(type_) == expected
