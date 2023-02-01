import typing
from platform import python_implementation

import typing_extensions

if python_implementation() == "PyPy":
    # MyPy doesn't support `ParamSpec` in `Protocol` 😮
    del typing.Protocol

if python_implementation() == "PyPy":
    typing.Protocol = typing_extensions.Protocol  # type: ignore[assignment]
