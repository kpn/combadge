# Models

In service interfaces, parameter and return types are _models_, which are used to forward arguments and validate responses.

## Response validation

As Combadge is aimed to support different 3rd-party clients, the backend classes convert raw responses into well-known intermediate representation, which the response would be able to parse. The representation is a typed dictionary, which depends on a specific application-level protocol. For example, HTTP backends normally provide such values as status code. See the application protocol documentation for available keys.

As Combadge is about API calls, there is a few fields that should be supported by any backend:

::: combadge.support.common.response
    options:
      heading_level: 3

## Supported types

Combadge is built on top of [Pydantic](https://docs.pydantic.dev/), hence Pydantic models are natively supported in service protocols.

However, thanks to the Pydantic's [`TypeAdapter`](https://docs.pydantic.dev/latest/api/type_adapter/), Combadge automatically supports:

### Standard [dataclasses](https://docs.python.org/3/library/dataclasses.html)

```python title="dataclasses.py" hl_lines="11-13 16-18 24 29"
from dataclasses import dataclass

from typing_extensions import Annotated, Protocol

from combadge.support.common.response import Body
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
    def post_anything(self, foo: Annotated[Request, Payload()]) -> Body[Response]:
        ...


backend = HttpxBackend(Client(base_url="https://httpbin.org"))
assert backend[Httpbin].post_anything(Request(42)) == Response(data='{"foo": 42}')
```

### [Typed dictionaries](https://docs.python.org/3/library/typing.html#typing.TypedDict)

```python title="typed_dict.py" hl_lines="9-10 13-14 20 25"
from typing_extensions import Protocol, TypedDict, Annotated

from combadge.support.common.response import Body
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
    def post_anything(self, foo: Annotated[Request, Payload()]) -> Body[Response]:
        ...


backend = HttpxBackend(Client(base_url="https://httpbin.org"))
assert backend[Httpbin].post_anything({"foo": 42}) == {"data": '{"foo": 42}'}
```
