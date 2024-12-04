---
tags:
  - HTTP
---

# Capturing HTTP status code

```python title="status_code.py" hl_lines="20 26"
import pytest
import sys

if sys.version_info < (3, 9):
    pytest.skip("HTTP 418 requires Python 3.9 or higher")

from http import HTTPStatus

from httpx import Client
from pydantic import BaseModel

from combadge.core.interfaces import SupportsService
from combadge.support.http.markers import http_method, path
from combadge.support.http.response import HttpStatus
from combadge.support.httpx.backends.sync import HttpxBackend


class Response(BaseModel):
    my_status_code: HTTPStatus


class SupportsHttpbin(SupportsService):
    @http_method("GET")
    @path("/status/418")
    def get_teapot(self) -> HttpStatus:
        raise NotImplementedError


backend = HttpxBackend(Client(base_url="https://httpbin.org"), raise_for_status=False)
service = SupportsHttpbin.bind(backend)

assert service.get_teapot() == HTTPStatus.IM_A_TEAPOT
```
