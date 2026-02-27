from ..state import State
from typing import AbstractSet, MutableSet
from ..transition_table import TransitionTable

def pre_add(state: State, states: AbstractSet[State]) -> None:
    if state not in states and state.label in {
        s.label for s in states
    }:
        raise ValueError(
            "Expected a state with a unique label. Got "
            f"duplicate label '{state.label}'."
        )
 
def pre_discard(
    state: State, 
    states: AbstractSet[State],
    initial_state: State,
    final_states: MutableSet[State],
    transition_table: TransitionTable,
) -> None:
    if state == initial_state:
        raise ValueError(
            f"Expected a non-initial state in the set of states {states}. "
            f"Got initial state {initial_state}."
        )
        
    final_states.discard(state)

    for (start_state, letter), next_states in list(
        transition_table.items()
    ):
        if start_state == state:
            del transition_table[(start_state, letter)]
        else:
            next_states.discard(state)