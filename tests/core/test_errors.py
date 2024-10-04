from asyncio import CancelledError

import pytest

from combadge.core.errors import BackendError


@pytest.mark.parametrize("inner_exception", [ValueError(42)])
def test_wrapped(inner_exception: BaseException) -> None:
    with pytest.raises(BackendError), BackendError:
        raise inner_exception


@pytest.mark.parametrize("inner_exception", [CancelledError()])
def test_non_wrapped(inner_exception: BaseException) -> None:
    with pytest.raises(type(inner_exception)), BackendError:
        raise inner_exception
