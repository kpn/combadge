from abc import abstractmethod
from typing import Any
from unittest.mock import MagicMock

from typing_extensions import Protocol

from combadge.binder import _enumerate_methods, bind
from combadge.interfaces import SupportsBindMethod, SupportsService


def test_enumerate_bindable_methods() -> None:
    """Test that bindable methods are returned."""

    class TestService(SupportsService):
        @abstractmethod
        def invoke(self) -> None:
            raise NotImplementedError

    assert list(_enumerate_methods(TestService)) == [("invoke", TestService.invoke)]


def test_enumerate_class_methods() -> None:
    """Test that class methods are ignored."""

    class TestService(SupportsService):
        @classmethod
        def ignored(cls) -> None:
            raise NotImplementedError

    assert list(_enumerate_methods(TestService)) == []


def test_enumerate_private_methods() -> None:
    """Test that «private» methods are ignored."""

    class TestService(SupportsService):
        def _ignored(cls) -> None:
            raise NotImplementedError

    assert list(_enumerate_methods(TestService)) == []


def test_bind() -> None:
    class TestProtocol(Protocol):
        @abstractmethod
        def call(self, request: Any) -> None:
            """Call the test protocol method."""
            raise NotImplementedError

    class Binder(SupportsBindMethod):
        def bind_method(self, _request_type: Any, _response_type: Any, _method: Any) -> MagicMock:
            return MagicMock(name="resolved_method")

    service = bind(TestProtocol, Binder())

    assert type(service).__name__ == "BoundService[TestProtocol]"
    assert type(service).__qualname__ == "bind.<locals>.BoundService[test_bind.<locals>.TestProtocol]"

    assert isinstance(service.call, MagicMock)
    assert service.call.__doc__ == TestProtocol.call.__doc__
