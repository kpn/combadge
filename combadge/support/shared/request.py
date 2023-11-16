from abc import ABC
from dataclasses import dataclass

from combadge._helpers.dataclasses import SLOTS


@dataclass(**SLOTS)
class BaseBackendRequest(ABC):  # noqa: B024
    """Base class for protocol-dependent requests."""
