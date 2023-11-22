# Do not repeat response annotations

Consider the following example. We have a service with 2 methods: `foo()` and `bar()`.

`foo()` declares its own response and error models:

```python
class Foo(SuccessfulResponse):
    ...


class FooError(ErrorResponse):
    status_code: Literal[HTTPStatus.IM_A_TEAPOT]
```

And so does `bar()`:

```python
class Bar(SuccessfulResponse):
    ...


class BarError(ErrorResponse):
    status_code: Literal[HTTPStatus.BAD_REQUEST]
```

In addition, they both share the following common error models:

```python
class InternalServerError(ErrorResponse):
    status_code: Literal[HTTPStatus.INTERNAL_SERVER_ERROR]


class ServiceUnavailable(ErrorResponse):
    status_code: Literal[HTTPStatus.SERVICE_UNAVAILABLE]
```

A head-on approach would be to declare the interface as follows:

```python
class Service(Protocol):
    def foo(self) -> Annotated[
        Union[Foo, FooError, InternalServerError, ServiceUnavailable],
        Mixin(StatusCode()),
    ]:
        ...

    def bar(self) -> Annotated[
        Union[Foo, BarError, InternalServerError, ServiceUnavailable],
        Mixin(StatusCode()),
    ]:
        ...
```

However, that way we would get a bunch of repetitive annotations. It is possible to extract the shared parts using the combination [`TypeAlias`](https://docs.python.org/3/library/typing.html#typing.TypeAlias) and `TypeVar`:

```python
ResponseT = TypeVar("ResponseT")
"""Method-specific response type."""

ErrorT = TypeVar("ErrorT")
"""Method-specific error type."""

CommonError: TypeAlias = Union[InternalServerError, ServiceUnavailable]
"""Any common error for all the methods."""

Response: TypeAlias = Annotated[
    Union[ResponseT, ErrorT, CommonError],
    Mixin(StatusCode()),
]


class Service(Protocol):
    def foo(self) -> Response[Foo, FooError]:
        ...

    def bar(self) -> Response[Bar, BarError]:
        ...
```
