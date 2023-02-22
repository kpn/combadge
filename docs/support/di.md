# Service container

## Overview

`#!python combadge.support.di.services` provides the ways to register bound service instances and reuse them across the code:

```python title="dependency_injection.py" hl_lines="25 27"
from typing import Any, List

from httpx import Client
from pydantic import BaseModel
from typing_extensions import Annotated, Protocol

from combadge.core.binder import bind
from combadge.support.di import services
from combadge.support.http.marks import QueryParam, http_method, path
from combadge.support.httpx.backends.sync import HttpxBackend


class Weather(BaseModel):
    current_condition: List[Any]


class SupportsWttrIn(Protocol):
    @http_method("GET")
    @path("/{in_}")
    def get_weather(self, *, in_: str, format_: Annotated[str, QueryParam("format")] = "j1") -> Weather:
        raise NotImplementedError


backend = HttpxBackend(Client(base_url="https://wttr.in"))
services[SupportsWttrIn] = bind(SupportsWttrIn, backend)
...
response = services[SupportsWttrIn].get_weather(in_="amsterdam")
assert response.current_condition
```

## Usage with [`pkgsettings`][with-pkgsettings]

Combining the service container with `#!python pkgsettings`, one can easier instantiate a service and register it via specifying just a handful of common client settings:

!!! note "Prerequisite"

    To enable the integration specify the `combadge[pkgsettings]` extra.

!!! warning "TODO"

    Not implemented.
