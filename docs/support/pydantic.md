# Pydantic

## Validation decorator

Combadge supports the [validation call](https://docs.pydantic.dev/latest/api/validate_call/) via the
`@wrap_with` marker:

```python
class SupportsWttrIn(Protocol):
    @wrap_with(validate_call)
    def get_weather(self, ...) -> ...:
        ...
```
