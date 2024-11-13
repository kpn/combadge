from abc import abstractmethod
from typing import Annotated, Any, Callable, Protocol, Union

import pytest
from httpx import AsyncClient, Client
from pydantic import BaseModel, Field

from combadge.core.errors import BackendError
from combadge.core.interfaces import SupportsService
from combadge.core.markers import Mixin
from combadge.support.http.markers import (
    CustomHeader,
    FormData,
    FormField,
    Header,
    QueryArrayParam,
    QueryParam,
    http_method,
    path,
)
from combadge.support.httpx.backends.async_ import HttpxBackend as AsyncHttpxBackend
from combadge.support.httpx.backends.sync import HttpxBackend as SyncHttpxBackend


@pytest.mark.vcr
def test_form_data() -> None:
    class Data(BaseModel):
        foo: int

    class Response(BaseModel):
        form: dict[str, Any]

    class SupportsHttpbin(SupportsService, Protocol):
        @http_method("POST")
        @path("/anything")
        @abstractmethod
        def post_anything(
            self,
            data: FormData[Data],
            bar: Annotated[int, FormField("barqux")],
            qux: Annotated[int, FormField("barqux")],
        ) -> Response: ...

    service = SupportsHttpbin.bind(SyncHttpxBackend(Client(base_url="https://httpbin.org")))
    response = service.post_anything(data=Data(foo=42), bar=100500, qux=100501)

    assert response == Response(form={"foo": "42", "barqux": ["100500", "100501"]})


@pytest.mark.vcr
def test_query_params() -> None:
    class Response(BaseModel):
        args: dict[str, Any]

    class SupportsHttpbin(SupportsService, Protocol):
        @http_method("GET")
        @path("/anything")
        @abstractmethod
        def get_anything(
            self,
            foo: Annotated[int, QueryParam("foobar")],
            bar: Annotated[int, QueryParam("foobar")],
            multivalue: Annotated[list[str], QueryArrayParam("multivalue")],
        ) -> Response: ...

    service = SupportsHttpbin.bind(SyncHttpxBackend(Client(base_url="https://httpbin.org")))
    response = service.get_anything(foo=100500, bar=100501, multivalue=["value1", "value2"])

    assert response == Response(args={"foobar": ["100500", "100501"], "multivalue": ["value1", "value2"]})


class _HeadersResponse(BaseModel):
    headers: dict[str, Any]
    content_length: int
    missing_header: int = 42


@pytest.mark.vcr
def test_headers_sync() -> None:
    class SupportsHttpbin(SupportsService, Protocol):
        @http_method("GET")
        @path("/headers")
        @abstractmethod
        def get_headers(
            self,
            foo: Annotated[str, CustomHeader("x-foo")],
            bar: Annotated[str, CustomHeader("x-bar")] = "barval",
            baz: Annotated[Union[str, Callable[[], str]], CustomHeader("x-baz")] = lambda: "bazval",
        ) -> Annotated[_HeadersResponse, Mixin(Header("content-length", "content_length"))]: ...

    service = SupportsHttpbin.bind(SyncHttpxBackend(Client(base_url="https://httpbin.org")))
    response = service.get_headers(foo="fooval")
    assert response.headers["X-Foo"] == "fooval"
    assert response.headers["X-Bar"] == "barval"
    assert response.headers["X-Baz"] == "bazval"
    assert response.content_length == 363
    assert response.missing_header == 42


@pytest.mark.vcr
async def test_headers_async() -> None:
    """
    Test custom headers in an asynchronous call.

    # TODO: I suspect that the separate test for `async` is not needed as the code does not care.
    """

    class SupportsHttpbin(SupportsService, Protocol):
        @http_method("GET")
        @path("/headers")
        @abstractmethod
        async def get_headers(
            self,
            foo: Annotated[str, CustomHeader("x-foo")],
            bar: Annotated[str, CustomHeader("x-bar")] = "barval",
            baz: Annotated[Union[str, Callable[[], str]], CustomHeader("x-baz")] = lambda: "bazval",
        ) -> Annotated[_HeadersResponse, Mixin(Header("content-length", "content_length"))]: ...

    service = SupportsHttpbin.bind(AsyncHttpxBackend(AsyncClient(base_url="https://httpbin.org")))
    response = await service.get_headers(foo="fooval")
    assert response.headers["X-Foo"] == "fooval"
    assert response.headers["X-Bar"] == "barval"
    assert response.headers["X-Baz"] == "bazval"
    assert response.content_length == 363
    assert response.missing_header == 42


@pytest.mark.vcr
def test_non_dict_json() -> None:
    class SupportsHttpbin(SupportsService, Protocol):
        @http_method("GET")
        @path("/get")
        @abstractmethod
        def get_non_dict(self) -> list[int]: ...

    # Since httpbin.org is not capable of returning a non-dict JSON,
    # I manually patched the recorded VCR.py response.
    service = SupportsHttpbin.bind(SyncHttpxBackend(Client(base_url="https://httpbin.org")))
    assert service.get_non_dict() == [42, 43]


@pytest.mark.vcr
def test_reraise_backend_error() -> None:
    """Test that an HTTPX error is properly reraised."""

    class SupportsHttpbin(SupportsService, Protocol):
        @http_method("GET")
        @path("/status/500")
        @abstractmethod
        def get_internal_server_error(self) -> None: ...

    service = SyncHttpxBackend(Client(base_url="https://httpbin.org"))[SupportsHttpbin]  # type: ignore[type-abstract]
    with pytest.raises(BackendError):
        service.get_internal_server_error()


@pytest.mark.vcr
def test_callback_protocol() -> None:
    """Test that the `__call__()` method can actually be used."""

    class Response(BaseModel):
        user_agent: Annotated[str, Field(validation_alias="user-agent")]

    class SupportsHttpbin(Protocol):
        @http_method("GET")
        @path("/user-agent")
        @abstractmethod
        def __call__(self) -> Response:
            raise NotImplementedError

    service = SyncHttpxBackend(Client(base_url="https://httpbin.org"))[SupportsHttpbin]  # type: ignore[type-abstract]
    assert service().user_agent == "python-httpx/0.27.2"
