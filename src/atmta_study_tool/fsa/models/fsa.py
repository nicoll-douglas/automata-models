from atmta_study_tool.language import Symbol
from .abstract_fsa import AbstractFSA


class FSA(AbstractFSA[Symbol]):
    """Represents a concrete Finite-State Automaton (FSA)."""

    def _validate_symbol(self, symbol: Symbol) -> None:
        """Validate that the given symbol is in the alphabet of the FSA."""
        super()._validate_symbol(symbol)

    def deterministic(self) -> bool:
        """Return True if the FSA is deterministic, otherwise False."""
        for state in self.states:
            for symbol in self.alphabet:
                if len(self.delta(state, symbol)) > 1:
                    return False

        return True
