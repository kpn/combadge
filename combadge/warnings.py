class CombadgeWarning(RuntimeWarning):
    """Base class for the package's warnings."""


class ServiceCallWarning(CombadgeWarning):
    """Something dubious has happened during the service call."""
