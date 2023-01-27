from abc import abstractmethod
from typing import Any, Callable

from pytest import mark, raises
from typing_extensions import Protocol

from combadge.binder import BaseBoundService, _enumerate_methods, _extract_types, _update_bound_service
from combadge.interfaces import SupportsService


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

    def missing_request(self) -> str:
        ...

    def too_many_parameters(self, request_1: Any, request_2: Any) -> None:
        ...


@mark.parametrize(
    ("method", "request_type", "response_type"),
    [
        (ExampleProtocol.valid_method, int, str),
    ],
)
def test_extract_types(method: Callable[..., Any], request_type: Any, response_type: Any) -> None:
    assert _extract_types(method) == (request_type, response_type)


@mark.parametrize(
    "method",
    [
        ExampleProtocol.missing_request,
        ExampleProtocol.too_many_parameters,
    ],
)
def test_extract_types_value_error(method: Callable[..., Any]) -> None:
    with raises(ValueError):
        _extract_types(method)
