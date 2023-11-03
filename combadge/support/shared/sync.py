from contextlib import AbstractContextManager
from typing import Callable, Generic

from combadge.core.typevars import BackendRequestT


class SupportsRequestWith(Generic[BackendRequestT]):  # noqa: D101
    def __init__(self, request_with: Callable[[BackendRequestT], AbstractContextManager]) -> None:  # noqa: D107
        self._request_with = request_with
