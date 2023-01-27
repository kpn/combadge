from typing import Any, Dict

from pytest import fixture


@fixture(scope="module")
def vcr_config() -> Dict[str, Any]:
    return {}
