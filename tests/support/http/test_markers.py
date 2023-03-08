from typing import Any

from combadge.support.http.abc import RequiresPath
from combadge.support.http.markers import _PathMarker


def test_path_format() -> None:
    mark = _PathMarker("/{foo}")
    request = RequiresPath.construct()
    mark.prepare_request(request, (), {"foo": "hello", "bar": "nope"})
    assert request.path == "/hello"


def test_path_factory() -> None:
    mark = _PathMarker(lambda foo, **__: f"/{foo}")
    request = RequiresPath.construct()
    mark.prepare_request(request, (), {"foo": "hello", "bar": "nope"})
    assert request.path == "/hello"
