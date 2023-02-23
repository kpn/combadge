from combadge.core.response import ErrorResponse


def test_error_inheritance() -> None:
    class Foo(ErrorResponse):
        pass

    class Bar(Foo):
        pass

    assert Bar.Error is not Foo.Error
    assert issubclass(Bar.Error, Foo.Error)
