from typing import TYPE_CHECKING, AbstractSet
from .states import states_contains

if TYPE_CHECKING:
    from ..models.state import State


def pre_set(initial_state: State, states: AbstractSet[State]) -> None:
    """Validate that the given initial state is in the given set of states.

    This hook is intended to run before the given initial state is set for an FSA.

    Args:
        initial_state: The new initial state being set for the FSA.
        states: The current set of states of an FSA.
    """
    states_contains(states, initial_state)
