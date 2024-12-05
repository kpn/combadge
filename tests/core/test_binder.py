from abc import abstractmethod
from typing import Any, Callable, Protocol

from combadge.core.binder import _enumerate_methods, _wrap
from combadge.core.markers.method import MethodMarker, wrap_with


def test_enumerate_bindable_methods() -> None:
    """Test that bindable methods are returned."""

    class TestService(Protocol):
        @abstractmethod
        def invoke(self) -> None:
            raise NotImplementedError

        @abstractmethod
        def __call__(self) -> None:
            raise NotImplementedError

    assert list(_enumerate_methods(TestService)) == [
        ("__call__", TestService.__call__),
        ("invoke", TestService.invoke),
    ]


def test_enumerate_class_methods() -> None:
    """Test that class methods are ignored."""

    class TestService(Protocol):
        @classmethod
        def ignored(cls) -> None:
            raise NotImplementedError

    assert list(_enumerate_methods(TestService)) == []


def test_enumerate_private_methods() -> None:
    """Test that «private» methods are ignored."""

    class TestService(Protocol):
        def _ignored(self) -> None:
            raise NotImplementedError

    assert list(_enumerate_methods(TestService)) == []


def test_decorator_ordering() -> None:
    """Verify that `@decorator` does not reverse the decorator execution order."""

    def decorate_1(what: Callable[[], tuple[Any, ...]]) -> Callable[[], tuple[Any, ...]]:
        return lambda: (1, *what())

    def decorate_2(what: Callable[[], tuple[Any, ...]]) -> Callable[[], tuple[Any, ...]]:
        return lambda: (2, *what())

    @wrap_with(decorate_1)
    @wrap_with(decorate_2)
    def get_actual() -> tuple[Any, ...]:
        return ()

    @decorate_1
    @decorate_2
    def get_expected() -> tuple[Any, ...]:
        return ()

    assert _wrap(get_actual, MethodMarker.ensure_markers(get_actual))() == get_expected()
