# Overview

[![Checks](https://img.shields.io/github/checks-status/kpn/combadge/main?logo=github)](https://github.com/kpn/combadge/actions/workflows/check.yaml)
[![Coverage](https://codecov.io/gh/kpn/combadge/branch/main/graph/badge.svg?token=ZAqYAaTXwE)](https://codecov.io/gh/kpn/combadge)
![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)
[![Python Version](https://img.shields.io/pypi/pyversions/combadge?logo=python&logoColor=yellow)](https://pypi.org/project/combadge/)
[![License](https://img.shields.io/github/license/kpn/combadge)](LICENSE)

!!! warning "This package is in active development"

    The documentatation is not good and complete as it should be, and the implementation may change drastically.

## Quick examples

=== "With HTTPX"

    ```python title="quickstart_httpx.py"
    from typing import List

    from httpx import Client
    from pydantic import BaseModel, Field
    from typing_extensions import Annotated, Protocol

    from combadge.core.binder import bind
    from combadge.support.http.marks import QueryParam, http_method, path
    from combadge.support.httpx.backends.sync import HttpxBackend


    # 1️⃣ Declare the response models:
    class CurrentCondition(BaseModel):
        humidity: int
        temperature: Annotated[float, Field(alias="temp_C")]


    class Weather(BaseModel):
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
    backend = HttpxBackend(Client(base_url="https://wttr.in"))
    service = bind(SupportsWttrIn, backend)

    # 🚀 Call the service:
    response = service.get_weather(in_="amsterdam")
    assert response.current[0].humidity == 71
    assert response.current[0].temperature == 8.0
    ```

=== "With Zeep"

    ```python title="quickstart_zeep.py"

    from typing import Literal, Union

    import zeep
    from pydantic import BaseModel, Field
    from pytest import raises
    from typing_extensions import Annotated

    from combadge.core.interfaces import SupportsService
    from combadge.core.response import FaultyResponse, SuccessfulResponse
    from combadge.support.http.marks import Body
    from combadge.support.soap.marks import operation_name
    from combadge.support.zeep.backends.sync import ZeepBackend


    # 1️⃣ Declare the request model:
    class NumberToWordsRequest(BaseModel, allow_population_by_field_name=True):
        number: Annotated[int, Field(alias="ubiNum")]


    # 2️⃣ Declare the response model:
    class NumberToWordsResponse(SuccessfulResponse):
        __root__: str


    # 3️⃣ Optionally, declare the error response models:
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

## Core principles

### Service protocol

In Combadge a definition of a service _protocol_ (also known as _interface_) is de-coupled from a service _implementation_. That allows a developer to define a service's interface and later bind it to a _backend_ which in turn is directly responsible for handling requests and responses.

To define a service protocol one makes use of the [PEP 544](https://peps.python.org/pep-0544/) aka «structural subtyping». Combadge inspects the protocol during «binding».

!!! tip "Using base `SupportsService`"

    Combadge can inspect any `Protocol`. But it might be a little beneficial to inherit from `#!python SupportsService` since it provides the `bind(to_backend)` method as a shorthand for `#!python bind(from_protocol, to_backend)`.

### Binding

In order to derive a service implementation, Combadge inspects a provided protocol and extract its methods and the method's signatures. The latter are used to derive request and response models.

Result of binding is a service class which encapsulates request and response handling.

### Models

Combadge models are based on [pydantic](https://docs.pydantic.dev/):

- A request is built and validated before it gets sent. The request's model is defined by the backend.
- A response is parsed based on the method's signature: what you annotate is what you get.

!!! tip "But what about errors?"

    In **pydantic** you can define a model as a `#!python typing.Union` of possible models: whichever validates first – that one gets returned. For us, it means that you can simply `#!python Union[...]` all possible successful and faulty models – and use the `#!python Union` as a return type.

Combadge does not restrict user in terms of model classes: as long as they are inherited from the `#!python BaseModel`, you are good to go. However, it may be easier to inherit from the predefined classes:

#### Base response

`#!python BaseResponse` is the lower-level API, one should consider inheriting from `#!python SuccessfulResponse` and `#!python FaultyResponse`. However, it is important to note its methods:

- `#!python raise_for_result()`: raises an error, if the response is faulty
- `#!python expect(exc_type_, *args)`: raises a specified error, if the response is faulty
- `#!python unwrap()`: combines everything in one handy method: returns a successful response, or raises an error if the response is faulty

!!! tip "That looks rusty, huh"

    The resemblance with Rust is not concidential: the author was inspired by [`std::result::Result`](https://doc.rust-lang.org/std/result/enum.Result.html).

The following response classes inherit from the `#!python BaseResponse`, which allows a user to use the methods above without any explicit error checks:

#### Successful response

`#!python SuccessfulResponse` implements the methods above so that they never fail.

#### Faulty response

The aforementioned methods always fail for `#!python FaultyResponse`. Furthermore, `#!python FaultyResponse` automatically derives distinct exception classes for each error model.

!!! tip "Error codes"

    Use [`typing.Literal`](https://docs.python.org/3/library/typing.html#typing.Literal) to define a separate error model for each error code.

### Marks

#### Method marks

#### Parameter marks

### Backends
