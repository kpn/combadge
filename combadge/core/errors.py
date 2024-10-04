from __future__ import annotations

from asyncio import CancelledError
from contextlib import AbstractContextManager
from types import TracebackType
from typing import Type


class CombadgeError(Exception):
    """Base error for any Combadge error."""


class _BackendErrorMeta(type, AbstractContextManager):
    """Makes class a context manager which re-raises any exceptions inside the context of itself."""

    def __exit__(  # type: ignore[misc]
        cls: Type[BaseException],  # noqa: N805
        exc_type: Type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
        /,
    ) -> None:
        # Wrapping `CancelledError` breaks `asyncio.TaskGroup`.
        if exc_value is not None and not isinstance(exc_value, CancelledError):
            raise cls(exc_value) from exc_value


class BackendError(CombadgeError, metaclass=_BackendErrorMeta):
    """
    Base error for any backend errors.

    Examples:
        Handling inner error:

        >>> try:
        >>>     client.method()
        >>> except BackendError as e:
        >>>     match e.inner:
        >>>         case httpx.TimeoutException():
        >>>             # Handle timeout error.
        >>>         case _:
        >>>             raise

        Wrapping client call (only needed for a new backend implementation):

        >>> with BackendError:
        >>>     ...
    """

    def __init__(self, inner: BaseException) -> None:
        """
        Instantiate the backend error.

        Args:
            inner: wrapped backend client exception
        """
        super().__init__(inner)

    @property
    def inner(self) -> BaseException:
        """Get the wrapped backend client exception."""
        return self.args[0]
