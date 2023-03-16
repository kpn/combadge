from typing import Any

from combadge.core.markers.method import MethodMarker
from combadge.support.soap.markers import _OperationNameMarker


def test_ensure_markers() -> None:
    def method() -> None:
        pass

    marks = MethodMarker.ensure_markers(method)
    assert marks == []

    mark = _OperationNameMarker[Any]("test")
    marks.append(mark)
    assert MethodMarker.ensure_markers(method) == [mark]
