---
hide:
  - navigation
---

# Core concepts

## Service protocol

In Combadge a definition of a service _protocol_ (also known as _interface_) is de-coupled from a service _implementation_. That allows a developer to define a service's interface and later bind it to a _backend_ which in turn is directly responsible for handling requests and responses.

To define a service protocol one makes use of the [PEP 544](https://peps.python.org/pep-0544/) aka «structural subtyping». Combadge inspects the protocol during «binding».

!!! tip "Using base `#!python SupportsService`"

    Combadge can inspect any `Protocol`. But it might be a little beneficial to inherit from `#!python SupportsService` since it provides the `bind(to_backend)` method as a shorthand for `#!python bind(from_protocol, to_backend)`.

## Binding

In order to derive a service implementation, Combadge inspects a provided protocol and extract its methods and the method's signatures. The latter are used to derive request and response models.

Result of binding is a service class which encapsulates request and response handling.

## Models

Combadge models are based on [pydantic](https://docs.pydantic.dev/):

- A request model is built and validated before it gets sent. Specific request model is defined by the backend.
- A response is parsed based on the method's signature: what you annotate is what you get.

Combadge does not restrict user in terms of response model classes: as long as they are inherited from the `#!python BaseModel`, you are good to go.

## Markers

**Markers** are named similarly to those from [pytest](https://docs.pytest.org/en/7.1.x/example/markers.html) and serve the same purpose: to «attach» a metadata that is needed to process a request or response.

### Method markers

**Method markers** are used to attach a metadata that is relevant to a whole request rather than a specific parameter.

Examples:

- HTTP method
- HTTP endpoint path
- SOAP operation name

!!! info ""

    Since there's no «native» way to mark a function in Python, the method markers are usually decorators that doesn't change a behaviour of a wrapped function.

### Parameter markers

Examples:

- Header: pass an argument as a specified headers value
- Query parameter: pass an argument as a specified query parameter
- Body: pass an argument as a request body

Parameter markers are specified with `#!python Annotated` type hints on corresponding parameters.

## Backends

**Backend** is a thin layer between a service instance and an actual client, which knows how to translate a protocol function's signature into an actual request and parse a response.
