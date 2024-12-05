# How it works

## Service protocol

In Combadge, a definition of a service _protocol_ (also known as _interface_) is de-coupled from a service _implementation_. That allows a developer to define a service's interface and later bind it to a [_backend_][backends] which in turn is directly responsible for handling requests and responses. It is possible to reuse the same protocol with multiple different backends.

To define a service protocol, one makes use of the [PEP 544](https://peps.python.org/pep-0544/) aka «structural subtyping». Combadge inspects the protocol during «binding».

## Binding

In order to derive a service implementation, Combadge inspects the provided protocol and extract its methods and the method's signatures – this is where all the magic happens. The latter are used to derive request and response models.

Result of the binding is a _service class_ which encapsulates request and response handling.

```mermaid
sequenceDiagram
    actor User

    box Combadge
        participant Binder
        participant Backend
    end
    Note over Backend: Adapts 3rd-party client<br>to Combadge's internal interfaces

    box 3rd-party
        participant Client
    end
    Note over Client: For example,<br>HTTPX, Requests, or Zeep

    User->>+Binder: Bind protocol
    loop Inspect methods
        Binder-->>Backend: Inspect
    end
    Binder-->Binder: Build service class
    create participant Service
    Binder->>+Service: Instantiate
    Service-->>-Binder: Bound service
    Binder-->>-User: Bound service
```

### Which methods are inspected?

- Non-private instance methods – methods which names do not start with `_` and accept `self` as a parameter.
- [`__call__`](https://docs.python.org/3/reference/datamodel.html#object.__call__) which allows calling a bound client directly. This may be useful when the protocol is meant to represent a single method and would otherwise just result in the name duplication.

## Calling a service method

```mermaid
sequenceDiagram
    box User
        actor User
        participant Service
    end
    Note over Service: Bound service instance

    box Combadge
        participant Backend
    end

    box 3rd-party
        participant Client
    end

    User->>+Service: Call service method
    Service-->Service: Build unified request object<br>from the arguments
    Service->>+Backend: Execute request
    Backend-->Backend: Build client-specific request object
    Backend->>+Client: Execute request
    Client-->>-Backend: Client-specific response object
    Backend-->>-Service: Unified response object
    Note over Service,Backend: Typed dictionary with<br>backend-specific response<br>For example, body or HTTP headers
    Service-->Service: Validate response
    Service-->>-User: Validated response
    Note over Service,User: For example, Pydantic model,<br>dataclass, or typed dictionary
```
