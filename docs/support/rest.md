# REST

## Recipes

### Avoiding request models for simple requests

There are cases when having a request model is undesired. For example, when a call takes a handful of simple
parameters of scalar types.

You can map such parameters with the [JsonField][combadge.support.rest.markers.JsonField] marker,
which would mark them as separate root fields of a JSON payload:

```python title="json_field.py"
from httpx import Client
from pydantic import BaseModel
from typing_extensions import Annotated, Protocol

from combadge.core.binder import bind
from combadge.support.http.markers import http_method, path
from combadge.support.httpx.backends.sync import HttpxBackend
from combadge.support.rest.markers import JsonField


class Response(BaseModel):
    data: str


class SupportsHttpbin(Protocol):
    @http_method("POST")
    @path("/anything")
    def post(self, *, foo: Annotated[str, JsonField("foobar")] = "quuuuux") -> Response:
        raise NotImplementedError


backend = HttpxBackend(Client(base_url="https://httpbin.org"))
service = bind(SupportsHttpbin, backend)

response = service.post()
assert response.data == r"""{"foobar": "quuuuux"}"""
```

## Markers

::: combadge.support.rest.markers
    options:
      heading_level: 3
      show_submodules: true
