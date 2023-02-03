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

ℹ️ This `README` is [tested](tests/integration/test_readme.py) and should run «as is».

```python
# test_id=quickstart

from typing import Literal, Union

import zeep
from pydantic import BaseModel, Field
from pytest import raises
from typing_extensions import Annotated

from combadge.core.interfaces import SupportsService
from combadge.core.response import FaultyResponse, SuccessfulResponse
from combadge.support.marks import Body
from combadge.support.soap.marks import operation_name
from combadge.support.zeep.backends.sync import ZeepBackend


# 1️⃣ Declare a request model:
class NumberToWordsRequest(BaseModel, allow_population_by_field_name=True):
    number: Annotated[int, Field(alias="ubiNum")]


# 2️⃣ Declare a response model:
class NumberToWordsResponse(SuccessfulResponse):
    __root__: str


# 3️⃣ Optionally, declare error response models:
class NumberTooLargeResponse(FaultyResponse):
    __root__: Literal["number too large"]


# 4️⃣ Declare the interface:
class SupportsNumberConversion(SupportsService):
    @operation_name("NumberToWords")
    def number_to_words(self, request: Body[NumberToWordsRequest]) -> Union[NumberTooLargeResponse, NumberToWordsResponse]:
        ...


# 5️⃣ Bind the service:
client = zeep.Client(wsdl="tests/integration/wsdl/NumberConversion.wsdl")
service = SupportsNumberConversion.bind(ZeepBackend(client.service))

# 🚀 Call the service:
response = service.number_to_words(NumberToWordsRequest(number=42))
assert response.unwrap().__root__ == "forty two "

# ☢️ Error classes are automatically derived for error models:
response = service.number_to_words(NumberToWordsRequest(number=-1))
with raises(NumberTooLargeResponse.Error):
    response.raise_for_result()
```
