import typing
from platform import python_implementation

if python_implementation() == "PyPy":
    # MyPy doesn't support `ParamSpec` in `Protocol` 😮
    del typing.Protocol

# It MUST be imported only after the `typing` attributes were deleted.
# Otherwise, it would just pick up the broken ones.
import typing_extensions

if python_implementation() == "PyPy":
    typing.Protocol = typing_extensions.Protocol  # type: ignore[assignment]
