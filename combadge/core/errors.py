from contextlib import contextmanager
from typing import Iterator

from pydantic import ValidationError


class BaseCombadgeError(Exception):
    """Base class for all our errors."""


class CombadgeValidationError(BaseCombadgeError):
    """Re-raised when Pydantic validation fails."""

    @classmethod
    @contextmanager
    def wrap(cls) -> Iterator[None]:  # noqa: D102
        try:
            yield
        except ValidationError as e:
            raise cls from e
