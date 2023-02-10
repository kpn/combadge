from typing import Any, Iterable, Mapping, Type, Union

from pydantic import validate_model
from typing_extensions import NoReturn

from combadge.core.binder import BaseBoundService, Signature
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
    call_args = bound_arguments.args
    call_kwargs = bound_arguments.kwargs

    # Construct an initial empty request without validation.
    # See also: https://github.com/pydantic/pydantic/issues/1864#issuecomment-679044432
    request = request_class.construct()

    # Apply the method marks: they receive all the arguments at once.
    for mark in signature.method_marks:
        mark.prepare_request(request, call_args, call_kwargs)

    # Apply the parameter marks: they receive their respective values.
    for name, mark in signature.parameter_marks:
        try:
            value = all_arguments[name]
        except KeyError:
            pass
        else:
            mark.prepare_request(request, value)

    # Validate and return the request.
    *_, error = validate_model(request_class, request.__dict__)
    if error:
        raise error
    return request
