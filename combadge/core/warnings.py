class CombadgeWarning(RuntimeWarning):
    """Base class for the package's warnings."""


class ResponseMarkNotSupported(CombadgeWarning):
    """The attribute's mark is unsupported by the backend."""
