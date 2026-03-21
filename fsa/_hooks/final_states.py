from typing import AbstractSet, TYPE_CHECKING
from .states import states_contains

if TYPE_CHECKING:
    from ..models.state import State


def pre_add(final_state: State, states: AbstractSet[State]) -> None:
    """Validate that the given final state is in the given set of states.

    This hook is intended to run before the given final state is added to the set of final states of an FSA.

    Args:
        final_state: The new final state being added to an FSA's set of final states.
        states: The current set of states (final and non-final) of the FSA.
    """
    states_contains(states, final_state)


# NOTE: When we set the final states of an FSA, a new observable set is created. So the pre_add hook is alled for each state in the new set of final states, thus, there is no need for a pre_set hook.
