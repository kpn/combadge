from contextlib import asynccontextmanager
from typing import AsyncIterator, TypeVar

_T = TypeVar("_T")


@asynccontextmanager
async def asyncnullcontext(enter_result: _T) -> AsyncIterator[_T]:
    yield enter_result
