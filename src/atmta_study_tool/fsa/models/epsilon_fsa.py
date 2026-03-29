from .abstract_fsa import AbstractFSA
from atmta_study_tool.language import Symbol, Word
from collections.abc import Set
from .state import State
from collections import deque
from atmta_study_tool._common.utils import validate_epsilon


class EpsilonFSA(AbstractFSA[Symbol | Word]):
    """Represents an FSA with epsilon transitions."""

    def _validate_symbol(self, symbol: Symbol | Word) -> None:
        """Validate that the given symbol is the alphabet or epsilon if it is a word."""
        if isinstance(symbol, Symbol):
            super()._validate_symbol(symbol)
        else:
            validate_epsilon(symbol)

    def epsilon_closure(self, states: Set[State]) -> set[State]:
        """Get the epsilon-closure of a set of states in the FSA.

        Args:
            states: The set of starting states from which to start considering epsilon transitions.

        Returns:
            The epsilon-closure which contains all states that can be reached by only following epsilon-transitions from the given states. At minimum this will be a set states including all the given states.
        """
        closure: set[State] = set(states)
        queue: deque[State] = deque(closure)

        while queue:
            current_state: State = queue.popleft()
            next_states: set[State] = self.delta(current_state, Word.EPSILON)

            for state in next_states:
                if state not in closure:
                    closure.add(state)
                    queue.append(state)

        return closure
