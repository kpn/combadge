from typing import Any, Dict

import pytest


@pytest.fixture(scope="module")
def vcr_config() -> Dict[str, Any]:
    return {}
