---
tags:
  - Markers
---

# Method

**Method markers** are used to attach a metadata that is relevant to a whole request rather than a specific parameter.

Examples:

- [HTTP method][combadge.support.http.markers.http_method]
- [HTTP endpoint path][combadge.support.http.markers.path]
- [SOAP operation name][combadge.support.soap.markers.operation_name]

!!! info ""

    Since there's no «native» way to mark a function in Python, the method markers are usually decorators that doesn't change a behaviour of a wrapped function.

## Core markers

Contrary to the support markers, the core markers are independent of application protocols or backends:

::: combadge.core.markers.method
    options:
      heading_level: 3
      members: ["wrap_with"]
