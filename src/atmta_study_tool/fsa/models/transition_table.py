from __future__ import annotations
from .state import State
from typing import override
from atmta_study_tool._common.data_structures import ObservableSet
from atmta_study_tool.language import Symbol
from collections.abc import Callable, Set, Iterable, Mapping, MutableMapping
from functools import reduce


class TransitionTable[S](
    MutableMapping[tuple[State, S | Symbol], ObservableSet[State]]
):
    """Represents the transition table for an automaton."""

    _data: dict[tuple[State, S | Symbol], ObservableSet[State]]
    # hook function to run before a state is set in the transition table either in a key or value
    _validate_state: Callable[[State], None] | None = None
    # hook function to run before a symbol is set in the transition table
    _validate_symbol: Callable[[S | Symbol], None] | None = None

    def __init__(
        self,
        mapping: Mapping[tuple[State, S], Set[State]] | None = None,
    ):
        if mapping is not None:
            for key, value in mapping.items():
                self[key] = value

    def _value(self, value: Iterable[State] | None = None) -> ObservableSet[State]:
        """Create an observable set with value-add and value-discard hooks for the given set of states."""
        # here we use lambdas to create closures and take advantage of late binding instead of passing direct attributes
        return ObservableSet[State](
            value,
            pre_add=lambda state: (
                None if self._validate_state is None else self._validate_state(state)
            ),
        )

    def _validate_key(self, key: tuple[State, S | Symbol]) -> None:
        if self._validate_state is not None:
            self._validate_state(key[0])

        if self._validate_symbol is not None:
            self._validate_symbol(key[1])

    def _validate_value(self, value: Set[State]) -> None:
        if self._validate_state is not None:
            for state in value:
                self._validate_state(state)

    @override
    def __getitem__(self, key: tuple[State, S | Symbol]) -> ObservableSet[State]:
        self._validate_key(key)

        if key in self._data:
            return self._data[key]

        return self.__missing__(key)

    @override
    def __setitem__(self, key: tuple[State, S | Symbol], value: Set[State]) -> None:
        self._validate_key(key)
        self._validate_value(value)

        self._data[key] = self._value(value)

    @override
    def __delitem__(self, key: tuple[State, S | Symbol]) -> None:
        self._validate_key(key)

        del self._data[key]

    def __missing__(self, key: tuple[State, S | Symbol]) -> ObservableSet[State]:
        value: ObservableSet[State] = self._value()
        self._data[key] = value

        return value

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    @override
    def __repr__(self):
        return f"{self.__class__.__name__}({self._data!r})"

    @override
    def __contains__(self, key: object) -> bool:
        return key in self._data

    def remove_such_that(
        self, match: Callable[[tuple[State, S | Symbol], ObservableSet[State]], bool]
    ) -> None:
        """Remove items from the transition table based on the given matching function.

        Args:
            match: A matching function that accepts the key and value of the current item being processed and that should return True if the item is to be discarded or False otherwise.
        """
        for key, value in list(self.items()):
            if match(key, value):
                del self[key]

    def transition_count(self, entity: S | Symbol | State | None = None) -> int:
        """Return the number of transitions in the transition table involving the given symbol, the given state, or in total if none given."""
        if entity is None:
            return reduce(lambda sum, v: len(v) + sum, self.values(), 0)

        if isinstance(entity, State):
            return (
                self.incoming_transition_count(entity)
                + self.loop_transition_count(entity)
                + self.outgoing_transition_count(entity)
            )

        if self._validate_symbol is not None:
            self._validate_symbol(entity)

        def _reducer(
            sum: int,
            table_item: tuple[tuple[State, S | Symbol], ObservableSet[State]],
        ) -> int:
            (_, transition_symbol), value = table_item

            if transition_symbol == entity:
                sum += len(value)

            return sum

        return reduce(
            _reducer,
            self.items(),
            0,
        )

    def incoming_transition_count(self, state: State) -> int:
        """Return the number of incoming transitions to the given state."""
        if self._validate_state is not None:
            self._validate_state(state)

        def _reducer(
            sum: int, item: tuple[tuple[State, S | Symbol], ObservableSet[State]]
        ) -> int:
            (start_state, _), next_states = item

            if state in next_states and start_state != state:
                sum += 1

            return sum

        return reduce(_reducer, self.items(), 0)

    def outgoing_transition_count(self, state: State) -> int:
        """Return the number of outgoing transitions from the given state."""
        if self._validate_state is not None:
            self._validate_state(state)

        def _reducer(
            sum: int, item: tuple[tuple[State, S | Symbol], ObservableSet[State]]
        ) -> int:
            (start_state, _), next_states = item

            if start_state == state:
                sum += len(next_states)

                # exclude the loop transition
                if state in next_states:
                    sum -= 1

            return sum

        return reduce(_reducer, self.items(), 0)

    def loop_transition_count(self, state: State) -> int:
        """Return the number of loop transitions at the given state."""
        if self._validate_state is not None:
            self._validate_state(state)

        def _reducer(
            sum: int, item: tuple[tuple[State, S | Symbol], ObservableSet[State]]
        ) -> int:
            (start_state, _), next_states = item

            if start_state == state and state in next_states:
                sum += 1

            return sum

        return reduce(_reducer, self.items(), 0)

    def flatten(self) -> set[tuple[State, S | Symbol, State]]:
        """Return a list of transitions in the transition table as a set of 3-tuples."""
        return {
            (start_state, transition, next_state)
            for (start_state, transition), next_states in self.items()
            for next_state in next_states
        }
