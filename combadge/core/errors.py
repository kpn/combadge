from __future__ import annotations

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
        __tracebackhide__ = True
        if exc_value is not None:
            raise cls(exc_value) from exc_value


class BackendError(CombadgeError, metaclass=_BackendErrorMeta):
    """
    Base error for any backend errors.

    Examples:
        >>> with BackendError:
        >>>     ...
    """
