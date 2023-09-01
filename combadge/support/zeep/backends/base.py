from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import Any, Generic, TypeVar, Union

try:
    from types import UnionType  # type: ignore[attr-defined]
except ImportError:
    # Before Python 3.10:
    UnionType = type(Union[int, str])  # type: ignore[assignment, misc]

from pydantic import RootModel
from typing_extensions import get_args as get_type_args
from typing_extensions import get_origin as get_type_origin
from zeep.exceptions import Fault
from zeep.helpers import serialize_object
from zeep.proxy import OperationProxy, ServiceProxy
from zeep.xsd import CompoundValue

from combadge.core.interfaces import ProvidesBinder
from combadge.core.typevars import ResponseT
from combadge.support.soap.response import BaseSoapFault, SoapFaultT

_ServiceProxyT = TypeVar("_ServiceProxyT", bound=ServiceProxy)
"""
Specific service proxy type returned by a Zeep client.

See Also:
    - https://docs.python-zeep.org/en/master/client.html#the-serviceproxy-object
"""

_OperationProxyT = TypeVar("_OperationProxyT", bound=OperationProxy)

_UNSET = object()


class BaseZeepBackend(ABC, ProvidesBinder, Generic[_ServiceProxyT, _OperationProxyT]):
    """Base class for the sync and async backends. Not intended for a direct use."""

    def __init__(self, service: _ServiceProxyT) -> None:
        """Instantiate the backend."""
        self._service = service

    @staticmethod
    def _split_response_type(response_type: Any) -> tuple[type[RootModel[Any]], type[RootModel[Any]]]:
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
            if isinstance(return_type, type) and issubclass(return_type, BaseSoapFault):
                # We should treat the return type as a SOAP fault type.
                fault_type = Union[fault_type, return_type] if fault_type is not _UNSET else return_type
            elif response_type is _UNSET:
                response_type = return_type
            else:
                response_type = Union[response_type, return_type]

        if response_type is _UNSET:
            response_type = None
        if fault_type is _UNSET:
            fault_type = BaseSoapFault

        # Since response type may be anything and union is not a model, we wrap them into root model.
        # Base SOAP fault should always be present as a fallback.
        return RootModel[response_type], RootModel[Union[fault_type, BaseSoapFault]]  # type: ignore[valid-type]

    def _get_operation(self, name: str) -> _OperationProxyT:
        """Get an operation by its name."""
        try:
            return self._service[name]
        except AttributeError as e:
            raise RuntimeError(f"available operations are: {dir(self._service)}") from e

    @staticmethod
    def _parse_response(value: CompoundValue, response_type: type[ResponseT]) -> ResponseT:
        """Parse the response value using the generic response types."""
        return response_type.model_validate(serialize_object(value, dict))

    @staticmethod
    def _parse_soap_fault(exception: Fault, fault_type: type[SoapFaultT]) -> SoapFaultT:
        """Parse the SOAP fault."""
        return fault_type.model_validate(exception.__dict__)


@dataclass
class ByBindingName:
    """Create service by binding name and address."""

    binding_name: str
    address: str


@dataclass
class ByServiceName:
    """Create service by service and port names."""

    service_name: str | None = None
    port_name: str | None = None
