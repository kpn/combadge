from combadge._helpers.pydantic import get_type_adapter
from combadge.support.common import Body


def test_validate_body() -> None:
    assert get_type_adapter(Body[str]).validate_python({"body": "hello"}) == "hello"
