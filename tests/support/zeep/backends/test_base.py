from __future__ import annotations

from sys import version_info
from typing import Union

import pytest
from pydantic import RootModel

from combadge.support.soap.response import BaseSoapFault
from combadge.support.zeep.backends.base import BaseZeepBackend


class _TestFault1(BaseSoapFault):
    ...


class _TestFault2(BaseSoapFault):
    ...


@pytest.mark.parametrize(
    ("response_type", "expected_response_type", "expected_fault_type"),
    [
        (int, RootModel[int], RootModel[BaseSoapFault]),
        (None, RootModel[None], RootModel[BaseSoapFault]),
        (
            Union[int, _TestFault1, _TestFault2],
            RootModel[int],
            RootModel[Union[_TestFault1, _TestFault2, BaseSoapFault]],
        ),
    ],
)
def test_split_response_type(response_type: type, expected_response_type: type, expected_fault_type: type) -> None:
    assert BaseZeepBackend._split_response_type(response_type) == (expected_response_type, expected_fault_type)


@pytest.mark.skipif(version_info < (3, 10), reason="PEP 604 required")
def test_split_response_type_pep_604() -> None:
    assert BaseZeepBackend._split_response_type(int | _TestFault1 | _TestFault2) == (  # type: ignore[operator]
        RootModel[int],
        RootModel[Union[_TestFault1, _TestFault2, BaseSoapFault]],
    )
