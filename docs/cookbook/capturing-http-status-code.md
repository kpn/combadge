---
tags:
  - HTTP
---

# Capturing HTTP status code

Status code can be «mixed» into a model by using a combination of the
[`Mixin`][combadge.core.markers.Mixin] and [`StatusCode`][combadge.support.http.markers.StatusCode] markers:

```python title="status_code.py" hl_lines="20 26"
import pytest
import sys

if sys.version_info < (3, 9):
    pytest.skip("HTTP 418 requires Python 3.9 or higher")

from http import HTTPStatus

from httpx import Client
from pydantic import BaseModel
from typing_extensions import Annotated

from combadge.core.interfaces import SupportsService
from combadge.core.markers import Mixin
from combadge.support.http.markers import StatusCode, http_method, path
from combadge.support.httpx.backends.sync import HttpxBackend


class Response(BaseModel):
    my_status_code: HTTPStatus


class SupportsHttpbin(SupportsService):
    @http_method("GET")
    @path("/status/418")
    def get_teapot(self) -> Annotated[Response, Mixin(StatusCode("my_status_code"))]:
        raise NotImplementedError


backend = HttpxBackend(Client(base_url="https://httpbin.org"), raise_for_status=False)
service = SupportsHttpbin.bind(backend)

response = service.get_teapot()
assert response.my_status_code == HTTPStatus.IM_A_TEAPOT
```
