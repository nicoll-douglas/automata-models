from __future__ import annotations
from .state import State
from typing import override, Mapping, Callable, AbstractSet
from utils import ObservableSet

class TransitionTable(dict):
    """Represents the transition table for an FSA."""

    _pre_setitem: OnItemHook | None
    _pre_value_add: OnValueMutateHook | None
    _pre_value_discard: OnValueMutateHook | None
    _post_value_add: OnValueMutateHook | None
    _post_value_discard: OnValueMutateHook | None

    type Key = tuple[State, str]
    type Value = ObservableSet[State]
    type OnItemHook = Callable[[Key, AbstractSet[State]], None]
    type OnValueMutateHook = Callable[[State], None]

    def __init__(
        self, 
        data: Mapping[Key, AbstractSet[State]] | None = None,
        pre_setitem: OnItemHook | None = None,
        pre_value_add: OnValueMutateHook | None = None,
        pre_value_discard: OnValueMutateHook | None = None,
        post_value_add: OnValueMutateHook | None = None,
        post_value_discard: OnValueMutateHook | None = None,
    ):
        """Initialise the transition table with the given states, 
        alphabet, and data.

        Args:
            states: A function that creates a StateSet object and gets passed 
            the current instance in order for the StateSet object to perform 
            automatic updates to the table when states change.

            alphabet: A function that creates an Alphabet object and gets 
            passed the current instance in order for the Alphabet object to 
            perform automatic updates to the table when the alphabet changes.

            data: Mapping data to add to the transition table. All and keys 
            and values must be valid according to the states and alphabet.
        """
        super().__init__()
    
        self._pre_setitem = pre_setitem
        self._pre_value_add = pre_value_add
        self._post_value_add = post_value_add
        self._pre_value_discard = pre_value_discard
        self._post_value_discard = post_value_discard

        if data is not None:
            for key, value in data.items():
                self[key] = value
        
    @override
    def __getitem__(self, key: Key) -> Value:
        return super().__getitem__(key)

    @override
    def __setitem__(self, key: Key, value: AbstractSet[State]) -> None:
        if self._pre_setitem is not None:
            self._pre_setitem(key, value)

        super().__setitem__(
            key, 
            ObservableSet[State](
                value,
                pre_add=self._pre_value_add,
                post_add=self._post_value_add,
                pre_discard=self._pre_value_discard,
                post_discard=self._post_value_discard
            )
        )
    
    def __missing__(self, key: Key) -> Value:
        """If the key is a valid key, return an empty set indicating 
        no end states for that transition."""
        self[key] = ObservableSet[State](
            pre_add=self._pre_value_add,
            post_add=self._post_value_add,
            pre_discard=self._pre_value_discard,
            post_discard=self._post_value_discard
        )

        return self[key]
