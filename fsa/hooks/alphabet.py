from ..fsa_renderer import FSARenderer
from ..transition_table import TransitionTable

def pre_add(new_letter: str) -> None:
    if new_letter == FSARenderer.EPSILON_LABEL:
        raise ValueError(
            f"Expected a string not equal to "
            f"'{FSARenderer.EPSILON_LABEL}' "
            f"(U+{ord(new_letter):04X}). Got '{new_letter}'."
        )
    
    if len(new_letter) != 1:
        raise ValueError(
            "Expected a string of length 1. "
            f"Got '{new_letter}'."
        )
    
def pre_discard(
    letter: str, 
    current_transition_table: TransitionTable
) -> None:
    for start_state, label in list(current_transition_table.keys()):
        if letter == label:
            del current_transition_table[(start_state, label)]
