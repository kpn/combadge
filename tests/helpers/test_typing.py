from sys import version_info
from typing import Annotated, Any

import pytest

from combadge._helpers.typing import unwrap_annotated, unwrap_type_alias


@pytest.mark.parametrize(
    ("type_", "expected"),
    [
        (None, None),
        (int, int),
        (Annotated[int, 42], int),
    ],
)
def test_unwrap_annotated(type_: Any, expected: Any) -> None:
    assert unwrap_annotated(type_) == expected


@pytest.mark.parametrize(
    ("type_", "expected"),
    [
        (None, None),
        (int, int),
    ],
)
def test_unwrap_type_alias_with_primitives(type_: Any, expected: Any) -> None:
    """Verify the function works with non-alias types."""
    assert unwrap_type_alias(type_) is expected


@pytest.mark.skipif(version_info < (3, 12), reason="PEP 695 required")
def test_unwrap_type_alias() -> None:
    """Verify with an actual alias."""
    exec("type Alias = int; assert unwrap_type_alias(Alias) is int", globals(), locals())
