"""Generic response models."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Type, Union

from pydantic import BaseModel
from typing_extensions import NoReturn, Self


class BaseResponse(ABC, BaseModel):
    """Base model representing any possible service response."""

    @abstractmethod
    def raise_for_result(self) -> Union[None, NoReturn]:
        """Raise an exception if the service call has failed."""
        raise NotImplementedError

    @abstractmethod
    def expect(self, exception_type: Type[BaseException], *args: Any) -> Union[None, NoReturn]:
        """Raise the specified exception if the service call has failed."""
        raise NotImplementedError

    @abstractmethod
    def unwrap(self) -> Union[Self, NoReturn]:
        """Return itself if the call was successful, raises an exception otherwise."""
        raise NotImplementedError


class SuccessfulResponse(BaseResponse):
    """
    Parent model for successful responses.

    Note:
        - May be used directly when no payload is expected.
    """

    def raise_for_result(self) -> None:
        """
        Do nothing.

        This call is a no-op since the response is successful.
        """

    def expect(self, _exception_type: Type[BaseException], *_args: Any) -> Union[None, NoReturn]:
        """Do nothing."""

    def unwrap(self) -> Self:
        """Return itself since there's no error."""
        return self


class FaultyResponse(BaseResponse, ABC):
    """
    Parent model for faulty responses (errors).

    Notes:
        - Useful when server returns errors in a free from (for example, an `<error>` tag).
        - Must be subclassed.
        - For SOAP Fault use or subclass the specialized `GenericSoapFault`.
    """

    class Error(Exception):
        """
        Dynamically derived exception class.

        The problem with `pydantic` is that you can't inherit from `BaseModel` and `Exception`
        at the same time. The workaround is to dynamically construct a derived exception class
        that is available via the class attribute and raised by `raise_for_result()`.
        """

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Build the derived exception class."""

        error_bases = tuple(base.Error for base in cls.__bases__ if issubclass(base, FaultyResponse))

        class DerivedException(*error_bases):  # type: ignore
            """
            Derived exception class.

            Notes:
                - This docstring is overridden by the corresponding model docstring.
            """

        DerivedException.__name__ = f"{cls.__name__}.Error"
        DerivedException.__qualname__ = f"{cls.__qualname__}.Error"
        DerivedException.__doc__ = cls.__doc__ or DerivedException.__doc__
        cls.Error = DerivedException  # type: ignore

    def raise_for_result(self) -> NoReturn:
        """Raise the derived exception."""
        raise self.Error

    def expect(self, exception_type: Type[BaseException], *args: Any) -> Union[None, NoReturn]:
        """Raise the specified exception with the derived exception context."""
        raise exception_type(*args) from self.Error

    def unwrap(self) -> NoReturn:
        """Raise the derived exception."""
        raise self.Error
