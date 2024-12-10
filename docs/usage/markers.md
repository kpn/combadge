# Markers

**Markers** are named similarly to those from [pytest](https://docs.pytest.org/en/7.1.x/example/markers.html) and serve the similar purpose: «attaching» metadata that is needed to build a request.

Examples:

- [HTTP method][combadge.support.http.request.http_method]
- [HTTP endpoint path][combadge.support.http.request.path]
- [SOAP operation name][combadge.support.soap.markers.operation_name]

!!! info "Implementation detail"

    Since there's no «native» way to mark a function in Python, the method markers are usually decorators that doesn't change a behaviour of a wrapped function.

## Core markers

The core markers are independent of application protocols or backends and always applicable:

::: combadge.core.markers
    options:
      heading_level: 3
      members: ["wrap_with"]
