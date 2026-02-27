from ..transition_table import TransitionTable
from ..state import State
from ..word import EPSILON
from typing import AbstractSet

def pre_setitem(
    key: TransitionTable.Key,
    value: AbstractSet[State],
    current_states: AbstractSet[State],
    current_alphabet: AbstractSet[str]
) -> None:
    state: State
    label: str
    state, label = key
    
    if state not in current_states:
        raise ValueError(
            f"Expected a state in the set of states {current_states}. "
            f"Got {state}."
        )
    
    if label not in current_alphabet and label != EPSILON:
        raise ValueError(
            f"Expected a letter in the alphabet {current_alphabet} or "
            f"epsilon. Got '{label}'."
        )
    
    if not value <= current_states:
        raise ValueError(
            f"Expected a subset of the set of states {current_states}. "
            f"Got {value}."
        )
    
def pre_value_add(
    new_state: State, 
    current_states: AbstractSet[State]
) -> None:
    if new_state not in current_states:
        raise ValueError(
            f"Expected a state in the set of states {current_states}. "
            f"Got {new_state}."
        )
