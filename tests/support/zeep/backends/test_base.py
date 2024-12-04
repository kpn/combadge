from __future__ import annotations

from sys import version_info
from typing import Union

import pytest

from combadge.support.soap.response import BaseSoapFault
from combadge.support.zeep.backends.base import BaseZeepBackend


class _TestFault1(BaseSoapFault): ...


class _TestFault2(BaseSoapFault): ...


@pytest.mark.parametrize(
    ("return_type", "expected_response_type", "expected_fault_type"),
    [
        (int, int, BaseSoapFault),
        (None, None, BaseSoapFault),
        (
            Union[int, _TestFault1, _TestFault2],
            int,
            Union[_TestFault1, _TestFault2, BaseSoapFault],
        ),
    ],
)
def test_split_return_type(return_type: type, expected_response_type: type, expected_fault_type: type) -> None:
    assert BaseZeepBackend._split_return_type(return_type) == (expected_response_type, expected_fault_type)


@pytest.mark.skipif(version_info < (3, 10), reason="PEP 604 required")
def test_split_return_type_pep_604() -> None:
    assert BaseZeepBackend._split_return_type(Union[int, _TestFault1, _TestFault2]) == (
        int,
        Union[_TestFault1, _TestFault2, BaseSoapFault],
    )
