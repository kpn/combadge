from typing import Any

from combadge.core.markers import Marker
from combadge.support.soap.markers import OperationName


def test_ensure_markers() -> None:
    def method() -> None:
        pass

    marks = Marker.ensure_markers(method)
    assert marks == []

    mark = OperationName[Any]("test")
    marks.append(mark)
    assert Marker.ensure_markers(method) == [mark]
