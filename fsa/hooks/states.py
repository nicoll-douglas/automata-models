from ..state import State
from typing import AbstractSet, MutableSet
from ..transition_table import TransitionTable

def pre_add(
    new_state: State, 
    current_states: AbstractSet[State]
) -> None:
    if new_state not in current_states and new_state.label in {
        s.label for s in current_states
    }:
        raise ValueError(
            "Expected a state with a unique label. Got "
            f"duplicate label '{new_state.label}'."
        )
 
def pre_discard(
    state: State, 
    current_states: AbstractSet[State],
    current_initial_state: State,
    current_final_states: MutableSet[State],
    current_transition_table: TransitionTable,
) -> None:
    if state == current_initial_state:
        raise ValueError(
            "Expected a non-initial state in the set of states "
            f"{current_states}. Got initial state {state}."
        )
        
    current_final_states.discard(state)

    for (start_state, letter), next_states in list(
        current_transition_table.items()
    ):
        if start_state == state:
            del current_transition_table[(start_state, letter)]
        else:
            next_states.discard(state)

def pre_set(
    new_states: AbstractSet[State], 
    current_initial_state: State
) -> None:
    if current_initial_state not in new_states:
        raise ValueError(
            "Expected a set containing the initial state "
            f"{current_initial_state}. Got {new_states}."
        )