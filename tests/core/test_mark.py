from typing import Any, List, Type

import pytest

from combadge.core.mark import ParameterMark, _extract_parameter_marks, _get_method_marks
from combadge.support.marks import _BODY_MARK, Body
from combadge.support.soap.marks import OperationNameMark


def test_get_method_marks() -> None:
    def method() -> None:
        pass

    marks = _get_method_marks(method)
    assert marks == []

    mark = OperationNameMark("test")
    marks.append(mark)
    assert _get_method_marks(method) == [mark]


@pytest.mark.parametrize(
    ("type_", "expected"),
    [
        (int, []),
        (Body[int], [_BODY_MARK]),
    ],
)
def test_extract_parameter_marks(type_: Type[Any], expected: List[ParameterMark]) -> None:
    assert _extract_parameter_marks(type_) == expected
