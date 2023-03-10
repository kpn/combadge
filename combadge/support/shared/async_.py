from contextlib import AbstractAsyncContextManager
from typing import Any, Callable


class SupportsRequestWith:  # noqa: D101
    def __init__(self, request_with: Callable[[Any], AbstractAsyncContextManager]) -> None:  # noqa: D107
        self._request_with = request_with
