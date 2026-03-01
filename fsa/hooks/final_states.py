from ..state import State
from typing import AbstractSet

def pre_add(
    new_final_state: State,
    current_states: AbstractSet[State]
) -> None:
    if new_final_state not in current_states:
        raise ValueError(
            "Expected a state in the set of states "
            f"{current_states}. Got {new_final_state}."
        )