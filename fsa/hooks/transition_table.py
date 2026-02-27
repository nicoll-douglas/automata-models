from ..transition_table import TransitionTable
from ..state import State
from ..word import EPSILON
from typing import Set

def pre_setitem(
    key: TransitionTable.Key,
    value: TransitionTable.Value,
    states: Set[State],
    alphabet: Set[str]
) -> None:
    state: State
    label: str
    state, label = key
    
    if state not in states:
        raise ValueError(
            f"Expected a state in the set of states {states}. "
            f"Got {state}."
        )
    
    if label not in alphabet and label != EPSILON:
        raise ValueError(
            f"Expected a letter in the alphabet {alphabet} or "
            f"epsilon. Got '{label}'."
        )
    
    if not value <= states:
        raise ValueError(
            f"Expected a subset of the set of states {states} "
            f"Got {value}."
        )
    
def pre_value_add(state: State, possible_states: Set[State]) -> None:
    if state not in possible_states:
        raise ValueError(
            f"Expected a state in the set of states {possible_states}. "
            f"Got {state}."
        )
