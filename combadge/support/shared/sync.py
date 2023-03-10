from contextlib import AbstractContextManager
from typing import Callable, Generic

from combadge.core.typevars import RequestT


class SupportsRequestWith(Generic[RequestT]):  # noqa: D101
    def __init__(self, request_with: Callable[[RequestT], AbstractContextManager]) -> None:  # noqa: D107
        self._request_with = request_with
