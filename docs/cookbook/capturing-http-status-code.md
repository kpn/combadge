# Capturing HTTP status code

```python title="status_code.py" hl_lines="19 25 32"
import pytest
import sys

if sys.version_info < (3, 9):
    pytest.skip("HTTP 418 requires Python 3.9 or higher")

from typing import Annotated
from http import HTTPStatus

from httpx import Client
from pydantic import AliasPath, BaseModel, Field

from combadge.core.interfaces import SupportsService
from combadge.support.http.markers import http_method, path
from combadge.support.httpx.backends.sync import HttpxBackend


class Response(BaseModel):
    my_status_code: Annotated[HTTPStatus, Field(validation_alias=AliasPath("http", "status"))]


class SupportsHttpbin(SupportsService):
    @http_method("GET")
    @path("/status/418")
    def get_teapot(self) -> Response:
        raise NotImplementedError


backend = HttpxBackend(Client(base_url="https://httpbin.org"), raise_for_status=False)
service = SupportsHttpbin.bind(backend)

assert service.get_teapot().my_status_code == HTTPStatus.IM_A_TEAPOT
```
