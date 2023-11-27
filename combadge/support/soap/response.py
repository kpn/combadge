"""Response extensions for SOAP."""

from typing import NoReturn, Optional

from combadge.core.response import ErrorResponse


class BaseSoapFault(ErrorResponse):
    """
    [SOAP Fault][1] error response model.

    [1]: https://www.w3.org/TR/2000/NOTE-SOAP-20000508/#_Toc478383507

    Note: This class is intended for use with the SOAP Fault specification
        For custom errors returned in a SOAP response body (such as `<error>` tag),
        subclass the `ErrorResponse`.

    Tip:
        SOAP backends should **always** fall back to `BaseSoapFault` if the actual SOAP fault
        does not match any of the protocol's return types.

        For client developers, this means that it is a good idea to include `BaseSoapFault`
        as the last possible `Union` variant to let users know that is should be handled.
    """

    code: str
    message: str

    def raise_for_result(self, exception: Optional[BaseException] = None) -> NoReturn:
        """Raise the derived error for this fault."""
        if not exception:
            raise self.Error(self)
        raise exception from self.Error(self)
