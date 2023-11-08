from typing import Any

from combadge.core.markers.response import Map, Mixin, ResponseMarker


def test_map() -> None:
    assert Map("key")(..., "payload") == {"key": "payload"}


def test_mixin() -> None:
    class InnerMarker1(ResponseMarker):
        def __call__(self, response: Any, payload: Any) -> Any:
            return {"inner1": "foo"}

    class InnerMarker2(ResponseMarker):
        def __call__(self, response: Any, payload: Any) -> Any:
            return {"inner2": "bar"}

    assert Mixin(InnerMarker1(), InnerMarker2())(..., {"outer": "qux"}) == {
        "inner1": "foo",
        "inner2": "bar",
        "outer": "qux",
    }
