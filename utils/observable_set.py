from collections.abc import MutableSet
from typing import override, Iterable, Iterator, Callable

class ObservableSet[T](MutableSet[T]):
    """Abstract base class representing a set that validates items 
    before insertion.
    """

    type Hook[U] = Callable[[U], None]

    # the underlying set data
    _data: set[T]
    _pre_add: Hook | None
    _pre_discard: Hook | None
    _post_add: Hook | None
    _post_discard: Hook | None

    def __init__(
        self, 
        iterable: Iterable[T] | None = None,
        pre_add: Hook[T] | None = None,
        pre_discard: Hook[T] | None = None,
        post_add: Hook[T] | None = None,
        post_discard: Hook[T] | None = None
    ):
        self._data = set()
        self._pre_add = pre_add
        self._pre_discard = pre_discard
        self._post_add = post_add
        self._post_discard = post_discard

        if iterable:
            for element in iterable:
                self.add(element)
    
    @override
    def add(self, element: T) -> None:
        if self._pre_add is not None:
            self._pre_add(element)

        self._data.add(element)

        if self._post_add is not None:
            self._post_add(element)

    @override
    def discard(self, element: T) -> None:
        if self._pre_discard is not None:
            self._pre_discard(element)

        self._data.discard(element)

        if self._post_discard is not None:
            self._post_discard(element)

    @classmethod
    def _from_iterable(cls, iterable: Iterable[T]) -> ObservableSet[T]:
        return cls(iterable)

    @override
    def __contains__(self, element: object) -> bool:
        return element in self._data

    @override
    def __len__(self) -> int:
        return len(self._data)

    @override
    def __iter__(self) -> Iterator[T]:
        return iter(self._data)

    @override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._data})"