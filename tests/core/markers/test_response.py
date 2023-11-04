from combadge.core.markers.response import Map


def test_map() -> None:
    assert Map("key").transform(..., "payload") == {"key": "payload"}
