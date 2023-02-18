# `combadge`

[![Checks](https://img.shields.io/github/checks-status/kpn/combadge/main?logo=github)](https://github.com/kpn/combadge/actions/workflows/check.yaml)
[![Coverage](https://codecov.io/gh/kpn/combadge/branch/main/graph/badge.svg?token=ZAqYAaTXwE)](https://codecov.io/gh/kpn/combadge)
![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)
[![Python Version](https://img.shields.io/pypi/pyversions/combadge?logo=python&logoColor=yellow)](https://pypi.org/project/combadge/)
[![License](https://img.shields.io/github/license/kpn/combadge)](LICENSE)

**📻 Application to the service, please respond!**

## Features

- [**Pydantic**](https://docs.pydantic.dev/)-based request and response models
- Automatically derived exception classes
- Using [**Protocol**](https://peps.python.org/pep-0544/)s to define service classes
- Built-in backends:
  - [HTTPX](https://www.python-httpx.org/), sync and async
  - [Zeep](https://docs.python-zeep.org/en/master/), sync and async
- Pluggable backends

## Documentation

<a href="https://kpn.github.io/combadge/">
    <img alt="Documentation" height="30em" src="https://img.shields.io/github/actions/workflow/status/kpn/combadge/docs.yml?label=documentation&logo=github">
</a>

## 🚀 Quick example

```python title="quickstart_httpx"

from typing import List

from httpx import Client
from pydantic import BaseModel, Field
from typing_extensions import Annotated, Protocol

from combadge.core.binder import bind
from combadge.support.httpx.backends.sync import HttpxBackend
from combadge.support.rest.marks import QueryParam, method, path


# 1️⃣ Declare the response models:
class CurrentCondition(BaseModel):
    humidity: int
    temperature: Annotated[float, Field(alias="temp_C")]


class Weather(BaseModel):
    current: Annotated[List[CurrentCondition], Field(alias="current_condition")]


# 2️⃣ Declare the protocol:
class SupportsWttrIn(Protocol):
    @method("GET")
    @path("/{in_}")
    def get_weather(
        self,
        *,
        in_: str,
        format_: Annotated[str, QueryParam("format")] = "j1",
    ) -> Weather:
        raise NotImplementedError


# 3️⃣ Bind the service:
backend = HttpxBackend(Client(base_url="https://wttr.in"))
service = bind(SupportsWttrIn, backend)

# 🚀 Call the service:
response = service.get_weather(in_="amsterdam")
assert response.current[0].humidity == 71
assert response.current[0].temperature == 8.0
```
