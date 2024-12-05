# Markers

**Markers** are named similarly to those from [pytest](https://docs.pytest.org/en/7.1.x/example/markers.html) and serve the same purpose: to «attach» a metadata that is needed to process a request or response.

## Method markers

**Method markers** are used to attach a metadata that is relevant to a whole request rather than a specific parameter.

Examples:

- [HTTP method][combadge.support.http.markers.http_method]
- [HTTP endpoint path][combadge.support.http.markers.path]
- [SOAP operation name][combadge.support.soap.markers.operation_name]

!!! info ""

    Since there's no «native» way to mark a function in Python, the method markers are usually decorators that doesn't change a behaviour of a wrapped function.

### Core markers

The core markers are independent of application protocols or backends and always applicable:

::: combadge.core.markers.method
    options:
      heading_level: 3
      members: ["wrap_with"]

## Parameter markers

Examples:

- Header: pass an argument as a specified headers value
- Query parameter: pass an argument as a specified query parameter
- Body: pass an argument as a request body

Parameter markers are specified with `#!python Annotated` type hints on corresponding parameters. See the relevant application protocol documentation for the applicable markers.
