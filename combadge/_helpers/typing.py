try:
    from types import UnionType  # type: ignore[attr-defined]
except ImportError:
    # Before Python 3.10:
    from typing import Union

    UnionType = type(Union[int, str])  # type: ignore[assignment, misc]
