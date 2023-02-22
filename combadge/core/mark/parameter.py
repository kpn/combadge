from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, List, Type

from typing_extensions import Annotated, get_origin
from typing_extensions import get_args as get_type_args

from combadge.core.typevars import RequestT


class ParameterMark(Generic[RequestT], ABC):
    """Parameter-specific mark that modifies a request with a call-time argument."""

    __slots__ = ()

    @staticmethod
    def extract(type_: Type[Any]) -> List[ParameterMark]:
        """Extract all parameter marks from the type annotation."""
        if get_origin(type_) is Annotated:
            return [arg for arg in get_type_args(type_) if isinstance(arg, ParameterMark)]
        return []

    @abstractmethod
    def prepare_request(self, request: RequestT, value: Any) -> None:
        """Update the request according to the mark and the actual argument."""
