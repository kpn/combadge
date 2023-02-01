"""Response extensions for SOAP."""

from typing import NoReturn, TypeVar

from combadge.core.response import FaultyResponse


class BaseSoapFault(FaultyResponse):
    """
    SOAP Fault model.

    Notes:
        - This class matches the SOAP Fault specification.
          For custom errors returned in a SOAP response body (such as `<error>` tag),
          subclass the `FaultyResponse`.

    See Also:
        - https://www.w3.org/TR/2000/NOTE-SOAP-20000508/#_Toc478383507
    """

    code: str
    message: str

    def raise_for_result(self) -> NoReturn:
        """Raise itself always."""
        raise self.Error(f"{self.code}: {self.message}")


SoapFaultT = TypeVar("SoapFaultT", bound=BaseSoapFault)
"""Specific SOAP Fault model type."""
