from contextlib import AbstractAsyncContextManager, asynccontextmanager
from sys import version_info
from typing import AsyncGenerator, Callable

if version_info >= (3, 10):
    from contextlib import nullcontext as asyncnullcontext
else:

    @asynccontextmanager  # type: ignore[no-redef]
    async def asyncnullcontext() -> AsyncGenerator[None, None]:
        yield None


class SupportsRequestWith:  # noqa: D101
    def __init__(self, request_with: Callable[[], AbstractAsyncContextManager]) -> None:  # noqa: D107
        self._request_with = request_with
