from abc import abstractmethod
from typing import Any, Callable, Protocol, Tuple
from unittest.mock import Mock

from typing_extensions import assert_type

from combadge.core.binder import _enumerate_methods, _wrap, bind
from combadge.core.interfaces import SupportsService
from combadge.core.markers.method import MethodMarker, wrap_with
from combadge.core.service import BaseBoundService


def test_enumerate_bindable_methods() -> None:
    """Test that bindable methods are returned."""

    class TestService(SupportsService, Protocol):
        @abstractmethod
        def invoke(self) -> None:
            raise NotImplementedError

    assert list(_enumerate_methods(TestService)) == [("invoke", TestService.invoke)]


def test_enumerate_class_methods() -> None:
    """Test that class methods are ignored."""

    class TestService(SupportsService, Protocol):
        @classmethod
        def ignored(cls) -> None:
            raise NotImplementedError

    assert list(_enumerate_methods(TestService)) == []


def test_enumerate_private_methods() -> None:
    """Test that «private» methods are ignored."""

    class TestService(SupportsService, Protocol):
        def _ignored(self) -> None:
            raise NotImplementedError

    assert list(_enumerate_methods(TestService)) == []


def test_decorator_ordering() -> None:
    """Verify that `@decorator` does not reverse the decorator execution order."""

    def decorate_1(what: Callable[[], Tuple[Any, ...]]) -> Callable[[], Tuple[Any, ...]]:
        return lambda: (1, *what())

    def decorate_2(what: Callable[[], Tuple[Any, ...]]) -> Callable[[], Tuple[Any, ...]]:
        return lambda: (2, *what())

    @wrap_with(decorate_1)
    @wrap_with(decorate_2)
    def get_actual() -> Tuple[Any, ...]:
        return ()

    @decorate_1
    @decorate_2
    def get_expected() -> Tuple[Any, ...]:
        return ()

    assert _wrap(get_actual, MethodMarker.ensure_markers(get_actual))() == get_expected()


def test_protocol_class_var() -> None:
    class ServiceProtocol(Protocol):
        ...

    service = bind(ServiceProtocol, Mock())  # type: ignore[type-abstract]
    assert isinstance(service, BaseBoundService)
    assert service.__combadge_protocol__ is ServiceProtocol


def test_service_type() -> None:
    class ServiceProtocol(SupportsService):
        ...

    service = ServiceProtocol.bind(Mock())
    assert_type(service, ServiceProtocol)
