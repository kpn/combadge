import inspect
from http import HTTPStatus
from typing import Any

import pytest
from httpx import Response

from combadge.support.http.abc import HttpRequestUrlPath
from combadge.support.http.markers import Header, Path, ReasonPhrase, StatusCode, Text


@pytest.mark.parametrize(
    ("format_", "call_args", "call_kwargs", "expected_path"),
    [
        ("/{keyword}", ("positional",), {"keyword": "keyword"}, "/keyword"),
        ("/{0}", ("positional",), {"keyword": "keyword"}, "/positional"),
        ("/{positional}", ("positional",), {"keyword": "keyword"}, "/positional"),
        ("/{positional}", (), {"positional": "positional_as_kwarg", "keyword": "keyword"}, "/positional_as_kwarg"),
    ],
)
def test_path_format(format_: str, call_args: tuple[Any, ...], call_kwargs: dict[str, Any], expected_path: str) -> None:
    mark = Path[Any](format_)
    request = HttpRequestUrlPath()
    mark.prepare_request(request, _example_signature.bind(*call_args, **call_kwargs))
    assert request.url_path == expected_path


def test_path_factory() -> None:
    mark = Path[Any](lambda _arguments: "don't care")
    request = HttpRequestUrlPath()
    mark.prepare_request(request, _example_signature.bind("positional", keyword="keyword"))
    assert request.url_path == "don't care"


def test_status_code() -> None:
    assert StatusCode("key")(Response(status_code=200), ...) == {"key": HTTPStatus.OK}


def test_reason_phrase() -> None:
    assert ReasonPhrase("key")(Response(status_code=200), ...) == {"key": "OK"}


def test_text() -> None:
    assert Text("key")(Response(status_code=200, text="my text"), ...) == {"key": "my text"}


def test_present_header() -> None:
    assert Header("x-foo", "key")(Response(200, headers={"X-Foo": "42"}), ...) == {"key": "42"}


def test_missing_header() -> None:
    assert Header("x-foo", "key")(Response(200, headers={}), ...) == {}


def _example(positional: str, *, keyword: str) -> None:
    pass


_example_signature = inspect.signature(_example)
