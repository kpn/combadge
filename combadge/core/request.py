from typing import Any, Iterable, Mapping, Type, TypeVar, Union

from pydantic import BaseModel, validate_model
from typing_extensions import NoReturn

from combadge.core.binder import BaseBoundService, Signature

RequestT = TypeVar("RequestT", bound=BaseModel)


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
    bound_arguments = signature.inner.bind(service, *call_args, **call_kwargs)
    bound_arguments.apply_defaults()
    arguments = bound_arguments.arguments

    request = request_class.construct()

    # Apply the method marks: they receive all the arguments at once.
    for mark in signature.method_marks:
        # TODO: pass `bound_arguments.args` too.
        mark.prepare_request(request, arguments)

    # Apply the parameter marks: they receive their respective values.
    for name, mark in signature.parameter_marks:
        try:
            value = arguments[name]
        except KeyError:
            pass
        else:
            mark.prepare_request(request, value)

    # Validate and return the request.
    # See also: https://github.com/pydantic/pydantic/issues/1864#issuecomment-679044432
    *_, error = validate_model(request_class, request.__dict__)
    if error:
        raise error  # TODO: introduce `CombadgeBaseError`.
    return request
