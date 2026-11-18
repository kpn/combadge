from abc import ABC
from dataclasses import dataclass


@dataclass(slots=True)
class BaseBackendRequest(ABC):  # noqa: B024
    """Base class for protocol-dependent requests."""
