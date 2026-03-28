from collections.abc import Iterable
from typing import Any


def guess_item_type(iterable: Iterable[Any]) -> type | None:
    """Guess and return the type of items in an iterable or None if empty."""
    if not iterable:
        return None

    return type(next(iter(iterable)))
