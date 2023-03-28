# Combadge

Combadge generates a service client implementation from a user service interface
declared by a [protocol](https://peps.python.org/pep-0544/) class or an abstract base class.

[![Checks](https://img.shields.io/github/checks-status/kpn/combadge/main?logo=github)](https://github.com/kpn/combadge/actions/workflows/check.yaml)
[![Coverage](https://codecov.io/gh/kpn/combadge/branch/main/graph/badge.svg?token=ZAqYAaTXwE)](https://codecov.io/gh/kpn/combadge)
![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)
[![Python Version](https://img.shields.io/pypi/pyversions/combadge?logo=python&logoColor=yellow)](https://pypi.org/project/combadge/)
[![License](https://img.shields.io/github/license/kpn/combadge)](LICENSE)

## Features

- Request and response models based on [**pydantic**](https://docs.pydantic.dev/)
- Declarative services using [`Protocol`](https://peps.python.org/pep-0544/)
- Exception classes automatically derived from error models
- Built-in backends:
    - [HTTPX](https://www.python-httpx.org/) – sync and async
    - [Zeep](https://docs.python-zeep.org/en/master/) – sync and async

## Documentation

<a href="https://kpn.github.io/combadge/">
    <img alt="Documentation" height="30em" src="https://img.shields.io/github/actions/workflow/status/kpn/combadge/docs.yml?label=documentation&logo=github">
</a>

## Sneak peek

```python title="quickstart_httpx.py"
from http import HTTPStatus
from typing import List

from httpx import Client
from pydantic import BaseModel, Field
from typing_extensions import Annotated, Protocol

from combadge.support.http.aliases import StatusCode
from combadge.support.http.markers import QueryParam, http_method, path
from combadge.support.httpx.backends.sync import HttpxBackend


# 1️⃣ Declare the response models:
class CurrentCondition(BaseModel):
    humidity: int
    temperature: Annotated[float, Field(alias="temp_C")]


class Weather(BaseModel):
    status: StatusCode[HTTPStatus]
    current: Annotated[List[CurrentCondition], Field(alias="current_condition")]


# 2️⃣ Declare the protocol:
class SupportsWttrIn(Protocol):
    @http_method("GET")
    @path("/{in_}")
    def get_weather(
        self,
        *,
        in_: str,
        format_: Annotated[str, QueryParam("format")] = "j1",
    ) -> Weather:
        raise NotImplementedError


# 3️⃣ Bind the service:
with HttpxBackend(Client(base_url="https://wttr.in"))[SupportsWttrIn] as service:
    # 🚀 Call the service:
    response = service.get_weather(in_="amsterdam")

assert response.status == HTTPStatus.OK
assert response.current[0].humidity == 71
assert response.current[0].temperature == 8.0
```
