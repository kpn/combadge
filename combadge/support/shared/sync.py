from contextlib import AbstractContextManager
from typing import Callable


class SupportsRequestWith:  # noqa: D101
    def __init__(self, request_with: Callable[[], AbstractContextManager]) -> None:  # noqa: D107
        self._request_with = request_with
