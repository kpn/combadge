from typing import Any

from combadge.core.markers.response import Map, Mixin, ResponseMarker


def test_map() -> None:
    assert Map("key")(..., "payload") == {"key": "payload"}


def test_mixin() -> None:
    class InnerMarker(ResponseMarker):
        def __call__(self, response: Any, payload: Any) -> Any:
            return {"inner": "foo"}

    assert Mixin(InnerMarker())(..., {"outer": "bar"}) == {
        "inner": "foo",
        "outer": "bar",
    }
