from typing import Any, Dict

from combadge.support.rest.abc import RequiresPath
from combadge.support.rest.marks import PathMark


def test_path_format() -> None:
    mark = PathMark("/{foo}")
    request: Dict[str, Any] = {}
    mark.prepare_request(request, {"foo": "hello", "bar": "nope"})
    assert RequiresPath(**request).path == "/hello"


def test_path_factory() -> None:
    mark = PathMark(lambda foo, **__: f"/{foo}")
    request: Dict[str, Any] = {}
    mark.prepare_request(request, {"foo": "hello", "bar": "nope"})
    assert RequiresPath(**request).path == "/hello"
