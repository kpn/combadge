from typing import Any, List, Type

import pytest
from typing_extensions import Annotated

from combadge.core.mark import MethodCallMark, ParameterMark
from combadge.support.http.headers import AcceptLanguage
from combadge.support.http.marks import Body, BodyParameterMark, Header, HeaderParameterMark
from combadge.support.soap.marks import _OperationNameMethodMark


def test_get_method_marks() -> None:
    def method() -> None:
        pass

    marks = MethodCallMark.set_default(method)
    assert marks == []

    mark = _OperationNameMethodMark("test")
    marks.append(mark)
    assert MethodCallMark.set_default(method) == [mark]


@pytest.mark.parametrize(
    ("type_", "expected"),
    [
        (int, []),
        (Body[int], [BodyParameterMark()]),
        (Annotated[str, Header("X-Header")], [HeaderParameterMark("X-Header")]),
        (AcceptLanguage[str], [HeaderParameterMark("Accept-Language")]),
    ],
)
def test_extract_parameter_marks(type_: Type[Any], expected: List[ParameterMark]) -> None:
    assert ParameterMark.extract(type_) == expected
