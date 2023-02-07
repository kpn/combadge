from typing import Any, Dict

from combadge.support.http.abc import RequiresPath
from combadge.support.http.marks import PathFactoryMark, PathFormatMark


def test_path_format() -> None:
    mark = PathFormatMark("/{foo}")
    request: Dict[str, Any] = {}
    mark.prepare_request(request, {"foo": "hello", "bar": "nope"})
    assert RequiresPath(**request).path == "/hello"


def test_path_factory() -> None:
    mark = PathFactoryMark(lambda foo, **__: f"/{foo}")
    request: Dict[str, Any] = {}
    mark.prepare_request(request, {"foo": "hello", "bar": "nope"})
    assert RequiresPath(**request).path == "/hello"
