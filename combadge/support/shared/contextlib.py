from contextlib import asynccontextmanager
from typing import AsyncIterator, TypeVar

_T = TypeVar("_T")


@asynccontextmanager
async def asyncnullcontext(enter_result: _T) -> AsyncIterator[_T]:
    """Compatibility with the older Python where `nullcontext` does not support async."""
    yield enter_result
