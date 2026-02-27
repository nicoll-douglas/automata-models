from ..fsa_renderer import FSARenderer
from ..transition_table import TransitionTable

def pre_add(letter: str) -> None:
    if letter == FSARenderer.EPSILON_LABEL:
        raise ValueError(
            f"Expected a string not equal to "
            f"'{FSARenderer.EPSILON_LABEL}' "
            f"(U+{ord(letter):04X}). Got '{letter}'."
        )
    
    if len(letter) != 1:
        raise ValueError(
            "Expected a string of length 1. "
            f"Got '{letter}'."
        )
    
def pre_discard(
    letter: str, 
    transition_table: TransitionTable
) -> None:
    for start_state, label in list(transition_table.keys()):
        if letter == label:
            del transition_table[(start_state, label)]
