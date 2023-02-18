from typing_extensions import Protocol

from combadge.support.di import services


def test_register_factory() -> None:
    # https://github.com/python/mypy/issues/4717
    services.register_factory(_SupportsService, _Service)  # type: ignore[type-abstract]
    assert isinstance(services[_SupportsService], _Service)  # type: ignore[type-abstract]
    assert services[_SupportsService] is not services[_SupportsService]  # type: ignore[type-abstract]


def test_register_singleton() -> None:
    service = _Service()
    services[_SupportsService] = service  # type: ignore[type-abstract]
    assert services[_SupportsService] is service  # type: ignore[type-abstract]


class _SupportsService(Protocol):
    """Test service protocol."""


class _Service(_SupportsService):
    """Test service class."""
