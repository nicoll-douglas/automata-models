from typing import AbstractSet, MutableSet, TYPE_CHECKING

if TYPE_CHECKING:
    from ..models.transition_table import TransitionTable
    from ..models.state import State


def states_contains(states: AbstractSet[State], state: State) -> None:
    """Validate that the given state is in the given set of states of an FSA.

    Args:
        states: The set of states of an FSA.
        state: A state to test.

    Raises:
        ValueError: On failed validation.
    """
    if state not in states:
        raise ValueError(
            f"Expected a state in the set of states {states}. Got {state!r}."
        )


def pre_discard(
    state: State,
    initial_state: State,
) -> None:
    """Validate that 'state' is not equivalent to 'initial_state', the initial state of an FSA.

    This hook is intended to run before 'state' is discarded from the set of states of an FSA.

    Args:
        state: A state being discarded from an FSA's set of states.
        initial_state: The initial state of the FSA.

    Raises:
        ValueError: On failed validation.
    """
    if state == initial_state:
        raise ValueError(f"Expected a non-initial state. Got initial state {state!r}.")


def post_discard(
    state: State,
    final_states: MutableSet[State],
    transition_table: TransitionTable,
) -> None:
    """Remove a state from the given set of final states (if it contains it), and any transitions from the given transition table that utilise the state.

    This hook is intended to run after the given state is discarded from the set of states of an FSA.

    Args:
        state: A state discarded from the set of states (final and non-final) of an FSA.
        final_states: The set of final states of the FSA.
        transition_table: The transition table of the FSA.
    """
    final_states.discard(state)

    transition_table.remove_such_that(lambda key, _: key[0] == state)

    for next_states in transition_table.values():
        next_states.discard(state)


def pre_set(states: AbstractSet[State], initial_state: State) -> None:
    """Validate that the given set of states contains the given initial state.

    This hook is intended to run before the given set of states are set for an FSA.

    Args:
        states: The set of states (final and non-final) being set for an FSA.
        initial_state: The initial state of the FSA.

    Raises:
        ValueError: On failed validation.
    """
    if initial_state not in states:
        raise ValueError(
            f"Expected a set of states containing the initial state {initial_state!r}. Got {states}."
        )


def post_set(
    states: AbstractSet[State],
    final_states: MutableSet[State],
    transition_table: TransitionTable,
) -> None:
    """Remove any states from the given set of final states that are not in the given set of states, and remove any transitions from the given transitition table that utilise a state not in the given set of states.

    This hooks is intended to run after the given set of states of an FSA is set.

    Args:
        states: The new set of states (final and non-final) set for an FSA.
        final_states: The current set of final states of the FSA.
        transition_table: The current transition table of the FSA.
    """
    final_states -= final_states - states

    transition_table.remove_such_that(lambda key, _: key[0] not in states)

    for next_states in transition_table.values():
        next_states -= next_states - states
