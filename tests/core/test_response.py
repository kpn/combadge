from combadge.core.response import ErrorResponse


def test_error_inheritance() -> None:
    class AnotherBaseError(Exception):
        """Example custom base exception class."""

    class Foo(ErrorResponse, exception_bases=(AnotherBaseError,)):
        pass

    class Bar(Foo):
        pass

    assert Bar.Error is not Foo.Error
    assert issubclass(Bar.Error, Foo.Error)
    assert issubclass(Foo.Error, AnotherBaseError)
    assert issubclass(Bar.Error, AnotherBaseError)
