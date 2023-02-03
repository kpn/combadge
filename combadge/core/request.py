from typing import Any, Dict, Iterable, Mapping, Type, TypeVar, Union

from pydantic import BaseModel
from typing_extensions import NoReturn

from combadge.core.binder import BaseBoundService, Signature

RequestT = TypeVar("RequestT", bound=BaseModel)


def build_request(
    type_: Type[RequestT],
    signature: Signature,
    service: BaseBoundService,
    call_args: Iterable[Any],
    call_kwargs: Mapping[str, Any],
) -> Union[RequestT, NoReturn]:
    """
    Build a request using the provided request type, marks, and service call arguments.

    Args:
        type_: target back-end request class
        signature: extracted description of the protocol service method
        service: an instance of a service class, on which the method is being called
        call_args: service method call positional arguments
        call_kwargs: service method call keyword arguments
    """
    arguments = signature.inner.bind(service, *call_args, **call_kwargs).arguments
    request: Dict[str, Any] = {}
    for mark in signature.method_marks:
        mark.prepare_request(request)
    for name, mark in signature.parameter_marks:
        try:
            value = arguments[name]
        except KeyError:
            pass
        else:
            mark.prepare_request(request, value)
    return type_.parse_obj(request)
