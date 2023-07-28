"""Generic response models."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, ClassVar, Generic, Iterable, NoReturn, Type

from pydantic import BaseModel
from typing_extensions import Self

from combadge.core.typevars import ResponseT


class BaseResponse(ABC, BaseModel):
    """
    Base model representing any possible service response.

    It's got a few abstract methods, which are then implemented by `SuccessfulResponse` and `ErrorResponse`.

    Notes:
        - `#!python BaseResponse` is the lower-level API,
          users should consider inheriting from `#!python SuccessfulResponse` and `#!python ErrorResponse`.
    """

    @abstractmethod
    def raise_for_result(self, exception: BaseException | None = None) -> None | NoReturn:
        """
        Raise an exception if the service call has failed.

        Raises:
            ErrorResponse.Error: an error derived from `ErrorResponse`

        Returns:
            always `None`

        Warning: Mypy does not recognize `NoReturn` here
            As of the time of writing, Mypy does not infer response type correctly
            after calling `response.raise_for_result()`.
            The `NoReturn` should suggest that `response` can only be a successful response
            (otherwise, the next line would be unreachable).

            The advice is to use [`unwrap()`][combadge.core.response.BaseResponse.unwrap]
            for the time being.
        """
        raise NotImplementedError

    @abstractmethod
    def unwrap(self) -> Self | NoReturn:
        """
        Return itself if the call was successful, raises an exception otherwise.

        This method allows «unpacking» a response with proper type hinting.
        The trick here is that all error responses' `unwrap()` are annotated with `NoReturn`,
        which suggests a type linter, that `unwrap()` may never return an error.

        Examples:
            >>> class MyResponse(SuccessfulResponse): ...
            >>>
            >>> class MyErrorResponse(ErrorResponse): ...
            >>>
            >>> class Service(Protocol):
            >>>     def call(self) -> MyResponse | MyErrorResponse: ...
            >>>
            >>> service: Service
            >>>
            >>> assert_type(service.call(), Union[MyResponse, MyErrorResponse])
            >>> assert_type(service.call().unwrap(), MyResponse)

        Raises:
            ErrorResponse.Error: an error derived from `ErrorResponse`

        Returns:
            always returns `Self`
        """
        raise NotImplementedError


class SuccessfulResponse(BaseResponse):
    """
    Parent model for successful responses.

    Users should not use it directly, but inherit their response models from it.
    """

    def raise_for_result(self, exception: BaseException | None = None) -> None:
        """
        Do nothing.

        This call is a no-op since the response is successful.
        """

    def unwrap(self) -> Self:
        """Return itself since there's no error."""
        return self


class BaseError(Generic[ResponseT], Exception):
    """Base exception class for all errors derived from `ErrorResponse`."""

    def __init__(self, response: ResponseT) -> None:
        """
        Instantiate the error.

        Args:
            response: original response that caused the exception
        """
        super().__init__(response)

    @property
    def response(self) -> ResponseT:
        """Get the response that caused the exception."""
        return self.args[0]


class ErrorResponse(BaseResponse, ABC):
    """
    Parent model for error responses.

    Users should not use it directly, but inherit their response models from it.
    """

    Error: ClassVar[Type[BaseError]] = BaseError
    """
    Dynamically derived exception class.

    For each model inherited from `ErrorResponse` Combadge generates an exception
    class, which is accessible through the `<ModelClass>.Error` attribute.

    Examples:
        >>> class InvalidInput(ErrorResponse):
        >>>     code: Literal["INVALID_INPUT"]
        >>>
        >>> try:
        >>>     service.call(...)
        >>> except InvalidInput.Error:
        >>>     ...

    Note: Why dynamically constructed class?
        The problem with `pydantic` is that you can't inherit from `BaseModel` and `Exception`
        at the same time. Thus, Combadge dynamically constructs a derived exception class,
        which is available via the class attribute and raised by `raise_for_result()` and `unwrap()`.
    """

    def __init_subclass__(cls, exception_bases: Iterable[type[BaseException]] = (), **kwargs: Any) -> None:
        """
        Build the derived exception class.

        Args:
            exception_bases: additional bases for the derived exception class
            kwargs: forwarded to the superclass
        """

        super().__init_subclass__(**kwargs)

        exception_bases = (
            # Inherit from the parent models' errors:
            *(base.Error for base in cls.__bases__ if issubclass(base, ErrorResponse)),
            # And from the user-provided ones:
            *exception_bases,
        )

        class DerivedException(*exception_bases):  # type: ignore
            """
            Derived exception class.

            Notes:
                - This docstring is overridden by the corresponding model docstring.
            """

        DerivedException.__module__ = cls.__module__
        DerivedException.__name__ = f"{cls.__name__}.Error"
        DerivedException.__qualname__ = f"{cls.__qualname__}.Error"
        DerivedException.__doc__ = cls.__doc__ or DerivedException.__doc__
        cls.Error = DerivedException  # type: ignore

    def raise_for_result(self, exception: BaseException | None = None) -> NoReturn:
        """
        Raise the derived exception.

        Args:
            exception: if set, raise the specified exception instead of the derived one.
        """
        if not exception:
            raise self.Error(self)
        raise exception from self.Error(self)

    def unwrap(self) -> NoReturn:
        """Raise the derived exception."""
        raise self.Error(self)
