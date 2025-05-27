# Models

Combadge is built on top of [Pydantic](https://docs.pydantic.dev/), hence Pydantic models are natively supported in service protocols.

However, thanks to the Pydantic's [`TypeAdapter`](https://docs.pydantic.dev/latest/api/type_adapter/), Combadge automatically supports:

## Built-in Python types

```python title="builtin.py" hl_lines="12 17"
from typing_extensions import Annotated, Protocol

from combadge.core.markers import Extract
from combadge.support.httpx.backends.sync import HttpxBackend
from combadge.support.http.markers import Payload, http_method, path
from httpx import Client


class Httpbin(Protocol):
    @http_method("POST")
    @path("/anything")
    def post_anything(self, foo: Payload[int]) -> Annotated[int, Extract("data")]:
        ...


backend = HttpxBackend(Client(base_url="https://httpbin.org"))
assert backend[Httpbin].post_anything(42) == 42
```

## Standard [dataclasses](https://docs.python.org/3/library/dataclasses.html)

```python title="dataclasses.py" hl_lines="10-12 15-17 23 28"
from dataclasses import dataclass

from typing_extensions import Protocol, Annotated

from combadge.support.httpx.backends.sync import HttpxBackend
from combadge.support.http.markers import Payload, http_method, path
from httpx import Client


@dataclass
class Request:
    foo: int


@dataclass
class Response:
    data: str


class Httpbin(Protocol):
    @http_method("POST")
    @path("/anything")
    def post_anything(self, foo: Payload[int]) -> Response:
        ...


backend = HttpxBackend(Client(base_url="https://httpbin.org"))
assert backend[Httpbin].post_anything(Request(42)) == Response(data='{"foo": 42}')
```

## [Typed dictionaries](https://docs.python.org/3/library/typing.html#typing.TypedDict)

```python title="typed_dict.py" hl_lines="8-9 12-13 19 24"
from typing_extensions import Protocol, TypedDict, Annotated

from combadge.support.httpx.backends.sync import HttpxBackend
from combadge.support.http.markers import Payload, http_method, path
from httpx import Client


class Request(TypedDict):
    foo: int


class Response(TypedDict):
    data: str


class Httpbin(Protocol):
    @http_method("POST")
    @path("/anything")
    def post_anything(self, foo: Payload[Request]) -> Response:
        ...


backend = HttpxBackend(Client(base_url="https://httpbin.org"))
assert backend[Httpbin].post_anything({"foo": 42}) == {"data": '{"foo": 42}'}
```
