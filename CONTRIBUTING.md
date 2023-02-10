### Structure

- Protocol-agnostic code should be placed under `combadge.core`.
- Protocol-specific code should be placed under the most generic subpackage inside `combadge.support`.
- Support subpackage may contain the following submodules:
  - `abc`: for abstract base classes, usually request mixins
  - `marks`: method or parameter marks (annotations)
  - `request`: concrete request classes for a specific protocol or backend

### Checklist

- When updating a backend, make sure to update its sync or async counterpart as well.
