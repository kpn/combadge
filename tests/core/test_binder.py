from abc import abstractmethod
from typing import Any, Callable, Mapping, Tuple, Type

from pytest import mark
from typing_extensions import Protocol

from combadge.core.binder import BaseBoundService, Signature, _enumerate_methods, _update_bound_service, _wrap
from combadge.core.interfaces import SupportsService
from combadge.core.markers.method import MethodMarker, decorator


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


@mark.parametrize(
    ("type_hints", "return_type"),
    [
        ({"return": str}, str),
    ],
)
def test_extract_return_type(type_hints: Mapping[str, Any], return_type: Type[Any]) -> None:
    assert Signature._extract_return_type(type_hints) == return_type


def test_decorator_ordering() -> None:
    """Verify that `@decorator` does not reverse the decorator execution order."""

    def decorate_1(what: Callable[[], Tuple[Any, ...]]) -> Callable[[], Tuple[Any, ...]]:
        return lambda: (1, *what())

    def decorate_2(what: Callable[[], Tuple[Any, ...]]) -> Callable[[], Tuple[Any, ...]]:
        return lambda: (2, *what())

    @decorator(decorate_1)
    @decorator(decorate_2)
    def get_actual() -> Tuple[Any, ...]:
        return ()

    @decorate_1
    @decorate_2
    def get_expected() -> Tuple[Any, ...]:
        return ()

    assert _wrap(get_actual, MethodMarker.ensure_markers(get_actual))() == get_expected()
