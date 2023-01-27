# `combadge`

> 📻 Application to the service, please respond!

[![Checks](https://img.shields.io/github/checks-status/kpn/combadge/main)](https://github.com/kpn/combadge/actions/workflows/check.yaml)
[![Coverage](https://codecov.io/gh/kpn/combadge/branch/main/graph/badge.svg?token=ZAqYAaTXwE)](https://codecov.io/gh/kpn/combadge)
![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)
[![License](https://img.shields.io/github/license/kpn/combadge)](LICENSE)

## Features

- [**Pydantic**](https://docs.pydantic.dev/)-based request and response models
- Automatically derived exception classes
- Using [**Protocol**](https://peps.python.org/pep-0544/)s to define service classes
- Built-in backends:
  - [Zeep](https://docs.python-zeep.org/en/master/), sync and async
- Pluggable backends

## 🚀 Quickstart

### 1️⃣ Declare a request model

```python
from typing import Annotated

from pydantic import BaseModel, Field


class NumberToWordsRequest(BaseModel):
    number: Annotated[int, Field(alias="ubiNum")]
```

### 2️⃣ Declare a response model

```python
from combadge.response import SuccessfulResponse


class NumberToWordsResponse(SuccessfulResponse):
    __root__: str
```

### 3️⃣ Optionally: declare error response models

```python
from typing import Literal

from combadge.response import FaultyResponse


class NumberTooLargeResponse(FaultyResponse):
    __root__: Literal["number too large"]
```

### 4️⃣ Declare the interface

```python
from combadge.decorators import soap_name
from combadge.interfaces import SupportsService


class SupportsNumberConversion(SupportsService):
    @soap_name("NumberToWords")
    def number_to_words(self, request: NumberToWordsRequest) -> NumberTooLargeResponse | NumberToWordsResponse:
        ...
```

### 5️⃣ Bind the service

```python
import zeep
from combadge.support.zeep.backends import ZeepBackend


client = zeep.Client(wsdl="NumberConversion.wsdl")
service = SupportsNumberConversion.bind(ZeepBackend(client.service))
```

### 🚀 Call the service

```python
response = service.number_to_words(NumberToWordsRequest(number=42))
assert response.unwrap().__root__ == "forty two "

response = service.number_to_words(NumberToWordsRequest(number=-1))
with raises(NumberTooLargeResponse.Error):
    response.raise_for_result()
```
