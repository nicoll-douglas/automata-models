from typing import AbstractSet, TYPE_CHECKING
from language.models.word import Word
from .states import states_contains

if TYPE_CHECKING:
    from ..models.transition_table import TransitionTable
    from ..models.state import State
    from language.models.alphabet import Alphabet
    from language.models.symbol import Symbol


# hook function to run before an item is set in the transition table of an FSA
def pre_setitem(
    key: TransitionTable.Key,
    value: AbstractSet[State],
    states: AbstractSet[State],
    alphabet: Alphabet,
) -> None:
    """Validate that the given key comprises a state in the given set of states, a symbol in given alphabet or equal to epsilon, and validate that the given value is a subset of the given set of states.

    This hook is intended to run before an the given key-value pair is set in the transition table of an FSA.

    Args:
        key: The key being set in the transition table of an FSA.
        value: The value being set for the key.
        states: The current set of states of the FSA.
        alphabet: The current alphabet of the FSA.

    Raises:
        ValueError: On failed validation.
    """
    start_state: State
    symbol: Symbol | Word
    start_state, symbol = key

    if start_state not in states:
        raise ValueError(
            f"Expected a start state in the set of states {states}. Got {start_state!r}."
        )

    if symbol not in alphabet and symbol != Word.EPSILON:
        raise ValueError(
            f"Expected a symbol in the alphabet {alphabet} or {Word.EPSILON}. Got {symbol!r}."
        )

    if not value <= states:
        raise ValueError(
            f"Expected the set of next states to be a subset of the set of states {states}. Got {value!r}."
        )


def pre_value_add(next_state: State, states: AbstractSet[State]) -> None:
    """Validate that the given next state (of an outgoing transition) is in the given set of states.

    This hook is intended to run before the given next state is added to the set of next states for an outgoing transition in the transition table of an FSA.

    Args:
        next_state: The 'next state' being added for an outgoing transition in an FSA.
        states: The current set of states of the FSA.
    """
    states_contains(states, next_state)
