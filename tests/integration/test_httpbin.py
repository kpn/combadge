from abc import abstractmethod
from typing import Any, Callable, Dict, List, Protocol, Union

from httpx import AsyncClient, Client
from pydantic import BaseModel
from pytest import mark
from typing_extensions import Annotated

from combadge.core.interfaces import SupportsService
from combadge.support.http.markers import CustomHeader, FormData, FormField, QueryParam, http_method, path
from combadge.support.httpx.backends.async_ import HttpxBackend as AsyncHttpxBackend
from combadge.support.httpx.backends.sync import HttpxBackend as SyncHttpxBackend


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

    service = SupportsHttpbin.bind(SyncHttpxBackend(Client(base_url="https://httpbin.org")))
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

    service = SupportsHttpbin.bind(SyncHttpxBackend(Client(base_url="https://httpbin.org")))
    response = service.get_anything(foo=100500, bar=100501)

    assert response == Response(args={"foobar": ["100500", "100501"]})


@mark.vcr
def test_headers_sync() -> None:
    class Response(BaseModel):
        headers: Dict[str, Any]

    class SupportsHttpbin(SupportsService, Protocol):
        @http_method("GET")
        @path("/headers")
        @abstractmethod
        def get_headers(
            self,
            foo: Annotated[str, CustomHeader("x-foo")],
            bar: Annotated[str, CustomHeader("x-bar")] = "barval",
            baz: Annotated[Union[str, Callable[[], str]], CustomHeader("x-baz")] = lambda: "bazval",
        ) -> Response:
            ...

    service = SupportsHttpbin.bind(SyncHttpxBackend(Client(base_url="https://httpbin.org")))
    response = service.get_headers(foo="fooval")
    assert response.headers["X-Foo"] == "fooval"
    assert response.headers["X-Bar"] == "barval"
    assert response.headers["X-Baz"] == "bazval"


@mark.vcr
async def test_headers_async() -> None:
    class Response(BaseModel):
        headers: Dict[str, Any]

    class SupportsHttpbin(SupportsService, Protocol):
        @http_method("GET")
        @path("/headers")
        @abstractmethod
        async def get_headers(
            self,
            foo: Annotated[str, CustomHeader("x-foo")],
            bar: Annotated[str, CustomHeader("x-bar")] = "barval",
            baz: Annotated[Union[str, Callable[[], str]], CustomHeader("x-baz")] = lambda: "bazval",
        ) -> Response:
            ...

    service = SupportsHttpbin.bind(AsyncHttpxBackend(AsyncClient(base_url="https://httpbin.org")))
    response = await service.get_headers(foo="fooval")
    assert response.headers["X-Foo"] == "fooval"
    assert response.headers["X-Bar"] == "barval"
    assert response.headers["X-Baz"] == "bazval"


@mark.vcr
def test_non_dict_json() -> None:
    class SupportsHttpbin(SupportsService, Protocol):
        @http_method("GET")
        @path("/get")
        @abstractmethod
        def get_non_dict(self) -> List[int]:
            ...

    # Since httpbin.org is not capable of returning a non-dict JSON,
    # I manually patched the recorded VCR.py response.
    service = SupportsHttpbin.bind(SyncHttpxBackend(Client(base_url="https://httpbin.org")))
    assert service.get_non_dict() == [42, 43]
