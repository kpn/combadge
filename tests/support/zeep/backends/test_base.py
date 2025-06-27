from __future__ import annotations

from typing import Union

import pytest

from combadge.support.soap.response import BaseSoapFault
from combadge.support.zeep.backends.base import BaseZeepBackend


class _TestFault1(BaseSoapFault): ...


class _TestFault2(BaseSoapFault): ...


@pytest.mark.parametrize(
    ("response_type", "expected_response_type", "expected_fault_type"),
    [
        (int, int, BaseSoapFault),
        (None, None, BaseSoapFault),
        (
            Union[int, _TestFault1, _TestFault2],  # noqa: UP007
            int,
            Union[_TestFault1, _TestFault2, BaseSoapFault],  # noqa: UP007
        ),
        (
            int | _TestFault1 | _TestFault2,
            int,
            Union[_TestFault1, _TestFault2, BaseSoapFault],  # noqa: UP007
        ),
    ],
)
def test_split_response_type(response_type: type, expected_response_type: type, expected_fault_type: type) -> None:
    assert BaseZeepBackend._split_response_type(response_type) == (expected_response_type, expected_fault_type)
