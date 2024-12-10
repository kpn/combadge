from __future__ import annotations

from abc import abstractmethod
from typing import Any, Protocol

from pydantic import BaseModel

from combadge.core.binder import BaseBoundService
from combadge.core.typevars import BackendT


class ServiceMethod(Protocol[BackendT]):
    """
    Bound method call specification.

    Usually implemented by a backend in its `bind_method`.
    """

    @abstractmethod
    def __call__(self, service: BaseBoundService[BackendT], /, *args: Any, **kwargs: Any) -> BaseModel:
        """
        Call the service method.

        Args:
            service: bound service instance
            args: positional request parameters
            kwargs: keyword request parameters

        Returns:
            Parsed response model.
        """
        raise NotImplementedError
