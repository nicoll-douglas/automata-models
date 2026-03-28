from ..types import StateLike
from ..models.state import State
from collections.abc import Iterable, Iterator


def state_from(state_like: StateLike) -> State:
    """Create and return a state from a state-like.

    If a state is passed then it is returned.
    """
    return State(state_like) if isinstance(state_like, str) else state_like


def states_from(state_likes: Iterable[StateLike]) -> Iterator[State]:
    """Create and yield states from state-likes.

    If a state is encountered then it is yielded.
    """
    for state_like in state_likes:
        yield state_from(state_like)
