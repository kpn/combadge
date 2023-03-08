from combadge.core.signature import Signature


def test_extract_return_type() -> None:
    def foo() -> str:
        return "bar"

    assert Signature.from_method(foo).return_type is str
