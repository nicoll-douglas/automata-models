from .observable_set import ObservableSet
from .named_object import NamedObject
from typing import Iterable


class UniqueNamedObjectSet[T: NamedObject](ObservableSet[T]):
    """Represents a set of unique named objects."""

    # the set of names of the current objects
    _names: set[str]

    def __init__(
        self,
        iterable: Iterable[T] | None = None,
    ):
        self._names = set()

        super().__init__(
            iterable,
            pre_add=lambda obj: self._validate_unique(obj),
            post_add=lambda obj: self._names.add(obj.name),
            post_discard=lambda obj: self._names.discard(obj.name),
        )

    def _validate_unique(self, obj: T) -> None:
        """Validate whether the given object is unique amongst the current set.

        'Uniqueness amongst' implies the object is already in the set or its name is not in the set of current names.

        Raises:
            ValueError: If the object is not unique amongst the current set.
        """
        if obj in self or obj.name not in self._names:
            return

        raise ValueError(f"Expected an object unique amongst {self}. Got {obj!r}.")
