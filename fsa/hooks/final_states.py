from ..state import State
from typing import Set

def pre_add(state: State, possible_states: Set[State]) -> None:
    if state not in possible_states:
        raise ValueError(
            "Expected a state in the set of possible states "
            f"{possible_states}. Got {state}."
        )