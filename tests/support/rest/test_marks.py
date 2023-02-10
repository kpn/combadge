from combadge.support.rest.abc import RequiresPath
from combadge.support.rest.marks import PathMark


def test_path_format() -> None:
    mark = PathMark("/{foo}")
    request = RequiresPath.construct()
    mark.prepare_request(request, (), {"foo": "hello", "bar": "nope"})
    assert request.path == "/hello"


def test_path_factory() -> None:
    mark = PathMark(lambda foo, **__: f"/{foo}")
    request = RequiresPath.construct()
    mark.prepare_request(request, (), {"foo": "hello", "bar": "nope"})
    assert request.path == "/hello"
