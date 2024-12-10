# Cookbook

## Capturing HTTP status code

Status code can be «mixed» into a model by using a combination of the
[`Mixin`][combadge.core.markers.Mixin] and [`StatusCode`][combadge.support.http.markers.StatusCode] markers:

```python title="status_code.py" hl_lines="20 26"
import pytest
import sys

if sys.version_info < (3, 9):
    pytest.skip("HTTP 418 requires Python 3.9 or higher")

from http import HTTPStatus
from typing import Protocol

from httpx import Client
from pydantic import BaseModel
from typing_extensions import Annotated

from combadge.core.markers import Mixin
from combadge.support.http.markers import StatusCode, http_method, path
from combadge.support.httpx.backends.sync import HttpxBackend


class Response(BaseModel):
    my_status_code: HTTPStatus


class SupportsHttpbin(Protocol):
    @http_method("GET")
    @path("/status/418")
    def get_teapot(self) -> Annotated[Response, Mixin(StatusCode("my_status_code"))]:
        raise NotImplementedError


backend = HttpxBackend(Client(base_url="https://httpbin.org"), raise_for_status=False)
service = backend[SupportsHttpbin]

response = service.get_teapot()
assert response.my_status_code == HTTPStatus.IM_A_TEAPOT
```

## Do not repeat response annotations

Consider the following example. We have a service with 2 methods: `foo()` and `bar()`.

`foo()` declares its own response and error models:

```python
class Foo(SuccessfulResponse):
    ...


class FooError(ErrorResponse):
    status_code: Literal[HTTPStatus.IM_A_TEAPOT]
```

And so does `bar()`:

```python
class Bar(SuccessfulResponse):
    ...


class BarError(ErrorResponse):
    status_code: Literal[HTTPStatus.BAD_REQUEST]
```

In addition, they both share the following common error models:

```python
class InternalServerError(ErrorResponse):
    status_code: Literal[HTTPStatus.INTERNAL_SERVER_ERROR]


class ServiceUnavailable(ErrorResponse):
    status_code: Literal[HTTPStatus.SERVICE_UNAVAILABLE]
```

A head-on approach would be to declare the interface as follows:

```python
class Service(Protocol):
    def foo(self) -> Annotated[
        Union[Foo, FooError, InternalServerError, ServiceUnavailable],
        Mixin(StatusCode()),
    ]:
        ...

    def bar(self) -> Annotated[
        Union[Foo, BarError, InternalServerError, ServiceUnavailable],
        Mixin(StatusCode()),
    ]:
        ...
```

However, that way we would get a bunch of repetitive annotations. It is possible to extract the shared parts using the combination [`TypeAlias`](https://docs.python.org/3/library/typing.html#typing.TypeAlias) and `TypeVar`:

```python
ResponseT = TypeVar("ResponseT")
"""Method-specific response type."""

ErrorT = TypeVar("ErrorT")
"""Method-specific error type."""

CommonError: TypeAlias = Union[InternalServerError, ServiceUnavailable]
"""Any common error for all the methods."""

Response: TypeAlias = Annotated[
    Union[ResponseT, ErrorT, CommonError],
    Mixin(StatusCode()),
]


class Service(Protocol):
    def foo(self) -> Response[Foo, FooError]:
        ...

    def bar(self) -> Response[Bar, BarError]:
        ...
```

## `Field`s for simple requests

There are cases when having a request model is undesired. For example, when a call takes a handful of simple
parameters of scalar types.

You can map such parameters with the [`Field`][combadge.support.http.markers.Field] marker,
which would mark them as separate root fields of the payload:

```python title="field.py" hl_lines="20"
from httpx import Client
from pydantic import BaseModel
from typing_extensions import Annotated, Protocol

from combadge.core.binder import bind
from combadge.support.http.markers import Field, http_method, path
from combadge.support.httpx.backends.sync import HttpxBackend


class Response(BaseModel):
    data: str


class SupportsHttpbin(Protocol):
    @http_method("POST")
    @path("/anything")
    def post(
        self,
        *,
        foo: Annotated[str, Field("foobar")] = "quuuuux",
    ) -> Response:
        raise NotImplementedError


backend = HttpxBackend(Client(base_url="https://httpbin.org"))
service = bind(SupportsHttpbin, backend)

response = service.post()
assert response.data == r"""{"foobar": "quuuuux"}"""
```

## Parameter validation

Combadge supports [`#!python @pydantic.validate_call`](https://docs.pydantic.dev/latest/api/validate_call/) via the
[`@wrap_with`][combadge.core.markers.method.wrap_with] marker:

```python
from combadge.core.markers.method import wrap_with


class SupportsWttrIn(Protocol):
    @wrap_with(validate_call)
    def get_weather(self, ...) -> ...:
        ...
```
