from abc import abstractmethod
from typing import Any, Callable

from pytest import mark
from typing_extensions import Protocol

from combadge.core.binder import BaseBoundService, _enumerate_methods, _extract_return_type, _update_bound_service
from combadge.core.interfaces import SupportsService


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
        def _ignored(self) -> None:
            raise NotImplementedError

    assert list(_enumerate_methods(TestService)) == []


def test_update_bound_service() -> None:
    class TestProtocol(Protocol):
        def call(self, request: Any) -> None:
            raise NotImplementedError

    class BoundService(BaseBoundService, TestProtocol):
        def call(self, request: Any) -> None:
            raise NotImplementedError

    _update_bound_service(BoundService, TestProtocol)

    assert BoundService.__name__ == "BoundService[TestProtocol]"
    assert BoundService.__qualname__ == (
        "test_update_bound_service.<locals>.BoundService[test_update_bound_service.<locals>.TestProtocol]"
    )


class ExampleProtocol(Protocol):
    def valid_method(self, request: int) -> str:
        ...


@mark.parametrize(
    ("method", "return_type"),
    [
        (ExampleProtocol.valid_method, str),
    ],
)
def test_extract_types(method: Callable[..., Any], return_type: Any) -> None:
    assert _extract_return_type(method) == return_type
