from pytest import raises

from combadge.core.response import BaseError, ErrorResponse


def test_error_inheritance() -> None:
    class AnotherBaseError(Exception):
        """Example custom base exception class."""

    class Foo(ErrorResponse, exception_bases=(AnotherBaseError,)):
        pass

    class Bar(Foo):
        pass

    assert Bar.Error is not Foo.Error
    assert issubclass(Foo.Error, BaseError)
    assert issubclass(Bar.Error, Foo.Error)
    assert issubclass(Foo.Error, AnotherBaseError)
    assert issubclass(Bar.Error, AnotherBaseError)


def test_default_raise_for_result() -> None:
    """Test `raise_for_result()` without the custom exception."""

    class Error(ErrorResponse):
        pass

    with raises(Error.Error):
        Error().raise_for_result()


def test_custom_raise_for_result() -> None:
    """Test `raise_for_result()` with the custom exception."""

    class Error(ErrorResponse):
        pass

    class CustomError(Exception):
        pass

    response = Error()
    with raises(CustomError) as e:
        response.raise_for_result(CustomError())

    assert isinstance(e.value.__cause__, Error.Error)
    assert e.value.__cause__.response is response


def test_derived_error_magic_attributes() -> None:
    class CustomError(ErrorResponse):
        pass

    assert CustomError.Error.__module__ == "tests.core.test_response"
    assert CustomError.Error.__name__ == "CustomError.Error"
    assert CustomError.Error.__qualname__ == "test_derived_error_magic_attributes.<locals>.CustomError.Error"
