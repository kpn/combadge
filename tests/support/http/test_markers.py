import inspect
from typing import Any, Dict, Tuple

from pytest import mark

from combadge.support.http.abc import RequiresPath
from combadge.support.http.markers import _PathMarker


@mark.parametrize(
    ("format_", "call_args", "call_kwargs", "expected_path"),
    [
        ("/{keyword}", ("positional",), {"keyword": "keyword"}, "/keyword"),
        ("/{0}", ("positional",), {"keyword": "keyword"}, "/positional"),
        ("/{positional}", ("positional",), {"keyword": "keyword"}, "/positional"),
        ("/{positional}", (), {"positional": "positional_as_kwarg", "keyword": "keyword"}, "/positional_as_kwarg"),
    ],
)
def test_format(format_: str, call_args: Tuple[Any, ...], call_kwargs: Dict[str, Any], expected_path: str) -> None:
    mark = _PathMarker[Any](format_)
    request = RequiresPath.model_construct()
    mark.prepare_request(request, _example_signature.bind(*call_args, **call_kwargs))
    assert request.path == expected_path


def test_factory() -> None:
    mark = _PathMarker[Any](lambda _arguments: "don't care")
    request = RequiresPath.model_construct()
    mark.prepare_request(request, _example_signature.bind("positional", keyword="keyword"))
    assert request.path == "don't care"


def _example(positional: str, *, keyword: str) -> None:
    pass


_example_signature = inspect.signature(_example)
