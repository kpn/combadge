from types import TracebackType
from typing import Any, Callable, ClassVar, Generic, Iterable, Optional, Type

from typing_extensions import Self

from combadge.core.typevars import BackendT


class BaseBoundService(Generic[BackendT]):
    """Base for dynamically generated service classes."""

    _protocol: ClassVar[Type]

    backend: BackendT
    __slots__ = ("backend",)

    def __init__(self, backend: BackendT) -> None:  # noqa: D107
        self.backend = backend

    @classmethod
    def __get_validators__(cls) -> Iterable[Callable[[Any], None]]:
        """
        Get validators for pydantic.

        Returns:
            No validators, this method only exists for compatibility with `@validate_arguments`.
        """
        return ()

    def __enter__(self) -> Self:
        self.backend.__enter__()  # type: ignore[attr-defined]
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Any:
        # Remove the freed instance from the cache:
        del self.backend[self._protocol]  # type: ignore[attr-defined]

        return self.backend.__exit__(exc_type, exc_value, traceback)  # type: ignore[attr-defined]

    async def __aenter__(self) -> Self:
        await self.backend.__aenter__()  # type: ignore[attr-defined]
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Any:
        # Remove the freed instance from the cache:
        del self.backend[self._protocol]  # type: ignore[attr-defined]

        return await self.backend.__aexit__(exc_type, exc_value, traceback)  # type: ignore[attr-defined]
