"""Response extensions for SOAP."""

from typing import NoReturn, Optional, TypeVar

from combadge.core.response import ErrorResponse


class BaseSoapFault(ErrorResponse):
    """
    SOAP Fault model.

    Notes:
        - This class matches the SOAP Fault specification.
          For custom errors returned in a SOAP response body (such as `<error>` tag),
          subclass the `ErrorResponse`.

    See Also:
        - https://www.w3.org/TR/2000/NOTE-SOAP-20000508/#_Toc478383507
    """

    code: str
    message: str

    def raise_for_result(self, exception: Optional[BaseException] = None) -> NoReturn:
        """Raise the derived error for this fault."""
        if not exception:
            raise self.Error(self)
        raise exception from self.Error(self)


SoapFaultT = TypeVar("SoapFaultT", bound=BaseSoapFault)
"""Specific SOAP Fault model type."""
