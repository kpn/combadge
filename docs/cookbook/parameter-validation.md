# Parameter validation

Combadge supports [`#!python @pydantic.validate_call`](https://docs.pydantic.dev/latest/api/validate_call/) via the
[`@wrap_with`][combadge.core.markers.method.wrap_with] marker:

```python
from combadge.core.markers.method import wrap_with


class SupportsWttrIn(Protocol):
    @wrap_with(validate_call)
    def get_weather(self, ...) -> ...:
        ...
```
