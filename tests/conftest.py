from typing import Any

import pytest


@pytest.fixture(scope="module")
def vcr_config() -> dict[str, Any]:
    return {}
