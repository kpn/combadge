from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from types import GenericAlias, UnionType
from typing import Any, Generic, TypeVar, Union
from typing import get_args as get_type_args
from typing import get_origin as get_type_origin

from annotated_types import SLOTS
from pydantic import HttpUrl, TypeAdapter
from pydantic_core import Url
from zeep.exceptions import Fault
from zeep.proxy import OperationProxy, ServiceProxy

from combadge._helpers.pydantic import get_type_adapter
from combadge.core.backend import BaseBackend
from combadge.core.errors import BackendError
from combadge.support.soap.response import BaseSoapFault

_ServiceProxyT = TypeVar("_ServiceProxyT", bound=ServiceProxy)
"""
Specific service proxy type returned by a Zeep client.

See Also:
    - https://docs.python-zeep.org/en/master/client.html#the-serviceproxy-object
"""

_OperationProxyT = TypeVar("_OperationProxyT", bound=OperationProxy)

_SoapFaultT = TypeVar("_SoapFaultT")
"""Specific SOAP Fault model type."""

_UNSET = object()


class BaseZeepBackend(BaseBackend, ABC, Generic[_ServiceProxyT, _OperationProxyT]):
    """Base class for the sync and async backends. Not intended for a direct use."""

    __slots__ = ("_service_cache", "_service")

    def __init__(self, service: _ServiceProxyT) -> None:
        """Instantiate the backend."""
        super().__init__()
        self._service = service

    @staticmethod
    def _split_response_type(response_type: Any) -> tuple[Any, Any]:
        """
        Split the response type into non-faults and faults.

        SOAP faults are handled separately, so we need to extract them from the annotated
        response type.
        """

        if get_type_origin(response_type) in (Union, UnionType):
            return_types = get_type_args(response_type)
        else:
            return_types = (response_type,)

        response_type: Any = _UNSET
        fault_type: Any = _UNSET

        for return_type in return_types:
            if (
                isinstance(return_type, type)
                and not isinstance(return_type, GenericAlias)  # remove when dropping Python 3.10
                and issubclass(return_type, BaseSoapFault)
            ):
                # We should treat the return type as a SOAP fault type.
                fault_type = fault_type | return_type if fault_type is not _UNSET else return_type
            elif response_type is _UNSET:
                response_type = return_type
            else:
                response_type = response_type | return_type

        if response_type is _UNSET:
            response_type = None
        if fault_type is _UNSET:
            fault_type = BaseSoapFault

        # Base SOAP fault should always be present as a fallback.
        return response_type, fault_type | BaseSoapFault

    @classmethod
    def _adapt_response_type(cls, response_type: Any) -> tuple[TypeAdapter[Any], TypeAdapter[Any]]:
        """Split the response type into non-faults and faults, and wrap them into the adapters."""
        response_type, fault_type = cls._split_response_type(response_type)
        return get_type_adapter(response_type), get_type_adapter(fault_type)

    def _get_operation(self, name: str) -> _OperationProxyT:
        """Get an operation by its name."""
        try:
            return self._service[name]
        except AttributeError as e:
            raise InvalidOperationError(e) from e

    @staticmethod
    def _parse_soap_fault(exception: Fault, fault_type: TypeAdapter[_SoapFaultT]) -> _SoapFaultT:
        """Parse the SOAP fault."""
        return fault_type.validate_python(exception.__dict__)


@dataclass(**SLOTS)
class ByBindingName:
    """
    Create service by binding name and address.

    Examples:
        >>> ByBindingName(
        >>>     binding_name="{http://www.dataaccess.com/webservicesserver/}NumberConversionSoapBinding",
        >>>     address=HttpUrl("https://www.dataaccess.com/webservicesserver/NumberConversion.wso",
        >>> )
    )
    """

    binding_name: str
    address: HttpUrl | Url | str

    @property
    def address_string(self) -> str:
        """Return the service address as a plain `#!python str`."""
        if isinstance(self.address, (HttpUrl, Url)):
            return str(self.address)
        return self.address


@dataclass(**SLOTS)
class ByServiceName:
    """
    Create service by service and port names.

    Examples:
        >>> ByServiceName(port_name="NumberConversionSoap")
    """

    service_name: str | None = None
    port_name: str | None = None


class InvalidOperationError(BackendError, RuntimeError):
    """Invalid operation is being called."""
