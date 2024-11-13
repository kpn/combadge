# Binding

In order to derive a service implementation, Combadge inspects the provided protocol and extract its methods and the method's signatures. The latter are used to derive request and response models.

Result of the binding is a service class which encapsulates request and response handling.

## Which methods are inspected?

- Non-private instance methods – methods which names do not start with `_` and accept `self` as a parameter.
- [`__call__`][1] which allows calling a bound client directly. This may be useful when the protocol is meant to represent a single method and would otherwise just result in the name duplication.

[1]: https://docs.python.org/3/reference/datamodel.html#object.__call__
