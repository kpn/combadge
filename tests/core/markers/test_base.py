from typing import Annotated, Any, TypeVar

import pytest

from combadge.core.markers import AnnotatedMarker, Map, Mixin
from combadge.support.http.markers import CustomHeader, Payload, StatusCode

AnyT = TypeVar("AnyT")


@pytest.mark.parametrize(
    ("type_", "expected"),
    [
        (int, []),
        (Payload[int], [Payload()]),
        (Annotated[str, CustomHeader("X-Header")], [CustomHeader("X-Header")]),
        (
            Annotated[AnyT | int, Mixin(StatusCode())][Annotated[int, Map("items")]],
            [Map("items"), Mixin(StatusCode())],
        ),
    ],
)
def test_extract(type_: type[Any], expected: list[AnnotatedMarker]) -> None:
    assert AnnotatedMarker.extract(type_) == expected
