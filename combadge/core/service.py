from typing import Any, Callable, Generic, Iterable

from combadge.core.typevars import BackendT


class BaseBoundService(Generic[BackendT]):
    """Parent of all bound service instances."""

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
