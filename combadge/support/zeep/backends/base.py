from abc import ABC
from typing import Any, Generic, Tuple, Type, TypeVar, Union

from pydantic import BaseModel, parse_obj_as
from typing_extensions import get_args as get_type_args
from typing_extensions import get_origin as get_type_origin
from zeep.exceptions import Fault
from zeep.helpers import serialize_object
from zeep.proxy import OperationProxy, ServiceProxy

from combadge.core.response import SuccessfulResponse
from combadge.core.typevars import ResponseT
from combadge.support.soap.response import BaseSoapFault, SoapFaultT

ServiceProxyT = TypeVar("ServiceProxyT", bound=ServiceProxy)
"""
Specific service proxy type returned by a Zeep client.

See Also:
    - https://docs.python-zeep.org/en/master/client.html#the-serviceproxy-object
"""

OperationProxyT = TypeVar("OperationProxyT", bound=OperationProxy)


class BaseZeepBackend(ABC, Generic[ServiceProxyT, OperationProxyT]):
    """Base class for the sync and async backends. Not intended for a direct use."""

    __slots__ = ("_service",)

    def __init__(self, service: ServiceProxyT) -> None:
        """Instantiate the backend."""
        self._service = service

    @staticmethod
    def _split_response_type(response_type: Type[Any]) -> Tuple[Type[BaseModel], Type[BaseSoapFault]]:
        """
        Split the response type into non-faults and faults.

        SOAP faults are handled separately, so we need to extract them from the annotated
        response type.
        """

        if get_type_origin(response_type) is Union:  # noqa: SIM108
            return_types = get_type_args(response_type)
        else:
            return_types = (response_type,)

        fault_type = BaseSoapFault

        response_type: Any = ...
        for return_type in return_types:
            if isinstance(return_type, type) and issubclass(return_type, BaseSoapFault):
                fault_type = Union[return_type, fault_type]  # type: ignore
            elif response_type is Ellipsis:
                response_type = return_type
            else:
                response_type = Union[response_type, return_type]  # type: ignore

        if response_type is Ellipsis:
            response_type = SuccessfulResponse

        return response_type, fault_type

    def _get_operation(self, name: str) -> OperationProxyT:
        """Get an operation by its name."""
        try:
            return self._service[name]
        except AttributeError as e:
            raise RuntimeError(f"available operations are: {dir(self._service)}") from e

    @staticmethod
    def _parse_response(value: Any, response_type: Type[ResponseT]) -> ResponseT:
        """Parse the response value using the generic response types."""
        return parse_obj_as(response_type, serialize_object(value, dict))

    @staticmethod
    def _parse_soap_fault(exception: Fault, fault_type: Type[SoapFaultT]) -> SoapFaultT:
        """Parse the SOAP fault."""
        return parse_obj_as(fault_type, exception.__dict__)
