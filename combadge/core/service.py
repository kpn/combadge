from typing import ClassVar, Generic

from combadge.core.typevars import BackendT


class BaseBoundService(Generic[BackendT]):
    """Base for dynamically generated service classes."""

    __combadge_protocol__: ClassVar[type]

    __combadge_backend__: BackendT
    __slots__ = ("__combadge_backend__",)

    def __init__(self, backend: BackendT) -> None:  # noqa: D107
        self.__combadge_backend__ = backend
