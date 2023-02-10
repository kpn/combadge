from combadge.support.rest.abc import RequiresPath
from combadge.support.rest.marks import _PathMark


def test_path_format() -> None:
    mark = _PathMark("/{foo}")
    request = RequiresPath.construct()
    mark.prepare_request(request, (), {"foo": "hello", "bar": "nope"})
    assert request.path == "/hello"


def test_path_factory() -> None:
    mark = _PathMark(lambda foo, **__: f"/{foo}")
    request = RequiresPath.construct()
    mark.prepare_request(request, (), {"foo": "hello", "bar": "nope"})
    assert request.path == "/hello"
