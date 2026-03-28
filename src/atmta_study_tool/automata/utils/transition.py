from atmta_study_tool._common.constants import EPSILON_UID
from atmta_study_tool.language import Word, Symbol
from ..types import Transition, TransitionLike


def validate_epsilon(obj: object) -> None:
    """Validate that the given object is epsilon if it is an instance of Word."""
    if isinstance(obj, Word) and obj != Word.EPSILON:
        raise ValueError(f"Expected the empty word {Word.EPSILON!r}. Got {obj!r}.")


def transition_from(transition_like: TransitionLike) -> Transition:
    """Create and return a transition from a transition-like.

    If a symbol or epsilon is passed then it is returned.

    Raise:
        ValueError: If transition_like is a Word and not equal to epsilon.
    """
    if isinstance(transition_like, str):
        return (
            Word.EPSILON if transition_like == EPSILON_UID else Symbol(transition_like)
        )

    validate_epsilon(transition_like)

    return transition_like
