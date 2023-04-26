from typing import Any, Iterable, Mapping, NoReturn, Type, Union

from pydantic import validate_model

from combadge.core.binder import BaseBoundService
from combadge.core.signature import Signature
from combadge.core.typevars import RequestT


def build_request(
    request_class: Type[RequestT],
    signature: Signature,
    service: BaseBoundService,
    call_args: Iterable[Any],
    call_kwargs: Mapping[str, Any],
) -> Union[RequestT, NoReturn]:
    """
    Build a request using the provided request type, marks, and service call arguments.

    Args:
        request_class: target back-end request class
        signature: extracted description of the protocol service method
        service: an instance of a service class, on which the method is being called
        call_args: service method call positional arguments
        call_kwargs: service method call keyword arguments
    """

    bound_arguments = signature.bind_arguments(service, *call_args, **call_kwargs)
    bound_arguments.apply_defaults()
    all_arguments = bound_arguments.arguments

    # Construct an initial empty request without validation.
    # See also: https://github.com/pydantic/pydantic/issues/1864#issuecomment-679044432
    request = request_class.construct()

    # Apply the method markers: they receive all the arguments at once.
    for marker in signature.method_markers:
        marker.prepare_request(request, bound_arguments)

    # Apply the parameter markers: they receive their respective values.
    for marker in signature.parameter_descriptors:
        try:
            value = all_arguments[marker.name]
        except KeyError:
            pass
        else:
            # allow for lazy loaded default parameters
            if callable(value):
                value = value()
            marker.prepare_request(request, value)

    # Validate and return the request.
    *_, error = validate_model(request_class, request.__dict__)
    if error:
        raise error
    return request
