# Pydantic

## Validation decorator

Combadge supports the [validation decorator](https://docs.pydantic.dev/usage/validation_decorator/) via the
`@wrap_with` marker:

```python
class SupportsWttrIn(Protocol):
    @wrap_with(validate_arguments)
    def get_weather(self, ...) -> ...:
        ...
```
