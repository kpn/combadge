from types import TracebackType
from typing import Any, ClassVar, Generic, Optional, Type

from typing_extensions import Self

from combadge.core.typevars import BackendT


class BaseBoundService(Generic[BackendT]):
    """Base for dynamically generated service classes."""

    __combadge_protocol__: ClassVar[Type]

    __combadge_backend__: BackendT
    __slots__ = ("__combadge_backend__",)

    def __init__(self, backend: BackendT) -> None:  # noqa: D107
        self.__combadge_backend__ = backend

    def __enter__(self) -> Self:
        self.__combadge_backend__.__enter__()  # type: ignore[attr-defined]
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Any:
        # Remove the freed instance from the cache:
        del self.__combadge_backend__[self.__combadge_protocol__]  # type: ignore[attr-defined]

        return self.__combadge_backend__.__exit__(exc_type, exc_value, traceback)  # type: ignore[attr-defined]

    async def __aenter__(self) -> Self:
        await self.__combadge_backend__.__aenter__()  # type: ignore[attr-defined]
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Any:
        # Remove the freed instance from the cache:
        del self.__combadge_backend__[self.__combadge_protocol__]  # type: ignore[attr-defined]

        return await self.__combadge_backend__.__aexit__(exc_type, exc_value, traceback)  # type: ignore[attr-defined]
