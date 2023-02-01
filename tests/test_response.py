from combadge.core.response import FaultyResponse


def test_error_inheritance() -> None:
    class Foo(FaultyResponse):
        pass

    class Bar(Foo):
        pass

    assert Bar.Error is not Foo.Error
    assert issubclass(Bar.Error, Foo.Error)
