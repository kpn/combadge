from typing import Any, List, Type

import pytest
from typing_extensions import Annotated

from combadge.core.markers import MethodMarker, ParameterMarker
from combadge.support.http.headers import AcceptLanguage
from combadge.support.http.markers import Body, BodyParameterMarker, Header, HeaderParameterMarker
from combadge.support.soap.markers import _OperationNameMethodMarker


def test_get_method_marks() -> None:
    def method() -> None:
        pass

    marks = MethodMarker.ensure_markers(method)
    assert marks == []

    mark = _OperationNameMethodMarker("test")
    marks.append(mark)
    assert MethodMarker.ensure_markers(method) == [mark]


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
