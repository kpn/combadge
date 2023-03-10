from contextlib import AbstractContextManager
from typing import Any, Callable


class SupportsRequestWith:  # noqa: D101
    def __init__(self, request_with: Callable[[Any], AbstractContextManager]) -> None:  # noqa: D107
        self._request_with = request_with
