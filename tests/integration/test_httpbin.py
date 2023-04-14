from abc import abstractmethod
from typing import Any, Dict

from httpx import Client
from pydantic import BaseModel
from pytest import mark
from typing_extensions import Annotated, Protocol

from combadge.core.interfaces import SupportsService
from combadge.support.http.markers import FormData, FormField, Header, QueryParam, http_method, path
from combadge.support.httpx.backends.sync import HttpxBackend


@mark.vcr
def test_form_data() -> None:
    class Data(BaseModel):
        foo: int

    class Response(BaseModel):
        form: Dict[str, Any]

    class SupportsHttpbin(SupportsService, Protocol):
        @http_method("POST")
        @path("/anything")
        @abstractmethod
        def post_anything(
            self,
            data: FormData[Data],
            bar: Annotated[int, FormField("barqux")],
            qux: Annotated[int, FormField("barqux")],
        ) -> Response:
            ...

    service = SupportsHttpbin.bind(HttpxBackend(Client(base_url="https://httpbin.org")))
    response = service.post_anything(data=Data(foo=42), bar=100500, qux=100501)

    assert response == Response(form={"foo": "42", "barqux": ["100500", "100501"]})


@mark.vcr
def test_query_params() -> None:
    class Response(BaseModel):
        args: Dict[str, Any]

    class SupportsHttpbin(SupportsService, Protocol):
        @http_method("GET")
        @path("/anything")
        @abstractmethod
        def get_anything(
            self,
            foo: Annotated[int, QueryParam("foobar")],
            bar: Annotated[int, QueryParam("foobar")],
        ) -> Response:
            ...

    service = SupportsHttpbin.bind(HttpxBackend(Client(base_url="https://httpbin.org")))
    response = service.get_anything(foo=100500, bar=100501)

    assert response == Response(args={"foobar": ["100500", "100501"]})


@mark.vcr
def test_headers() -> None:
    class Response(BaseModel):
        headers: Dict[str, Any]

    class SupportsHttpbin(SupportsService, Protocol):
        @http_method("GET")
        @path("/headers")
        @abstractmethod
        def get_headers(
            self,
            foo: Annotated[str, Header("x-foo")],
            bar: Annotated[str, Header("x-bar")] = "barval",
        ) -> Response:
            ...

    service = SupportsHttpbin.bind(HttpxBackend(Client(base_url="https://httpbin.org")))
    response = service.get_headers(foo="fooval")
    assert response.headers["X-Foo"] == "fooval"
    assert response.headers["X-Bar"] == "barval"
