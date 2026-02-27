from __future__ import annotations
from collections import deque, defaultdict
from typing import Set, Callable
from .state import State
from .word import EPSILON
from .transition_table import TransitionTable
from .utils import subset_construction
from . import hooks
from utils import ObservableSet

class FSA:
    """Represents a finite-state automaton (FSA) and contains algorithms 
    that operate on it."""

    _initial_state: State
    _states: ObservableSet[State]
    _final_states: ObservableSet[State]
    _transition_table: TransitionTable
    _alphabet: ObservableSet[str]

    def __init__(
        self,
        initial_state: State,
        states: Set[State],
        alphabet: Set[str] | None = None,
        transitions: Set[tuple[State, str, State]] | None = None,
        final_states: Set[State] | None = None
    ):
        self._initial_state = initial_state
        self._alphabet = self._alphabet_from_set(alphabet)
        self._final_states = self._final_states_from_set(final_states)

        self._states = ObservableSet[State](
            states,
            pre_add=lambda state: hooks.states.pre_add(state, self.states),
            pre_discard=lambda state: hooks.states.pre_discard(
                state=state,
                states=self.states,
                initial_state=self.initial_state,
                final_states=self.final_states,
                transition_table=self.transition_table
            )
        )
        self._alphabet = ObservableSet[str](
            alphabet,
            pre_add=lambda letter: hooks.alphabet.pre_add(letter),
            pre_discard=lambda letter: hooks.alphabet.pre_discard(
                letter=letter, 
                transition_table=self.transition_table
            ),
        )
        self._transition_table = TransitionTable(
            (
                {
                    (start_state, label): end_state
                    for start_state, label, end_state
                    in transitions
                }
                if transitions
                else None
            ),
            pre_setitem=(
                lambda key, value: hooks.transition_table.pre_setitem(
                    key=key,
                    value=value,
                    states=self.states,
                    alphabet=self.alphabet
                )
            ),
            pre_value_add=lambda state: hooks.transition_table.pre_value_add(
                state=state,
                possible_states=self.states
            ),
        )

    @property
    def states(self) -> ObservableSet[State]:
        """Get the FSA's set of states."""
        return self._states
    
    @property
    def initial_state(self) -> State:
        return self._initial_state
    
    @initial_state.setter
    def initial_state(self, value: State) -> None:
        if value not in self.states:
            raise ValueError(
                f"Expected a state in the set of states {self.states}. "
                f"Got {value}."
            )
        
        self._initial_state = value
    
    @property
    def final_states(self) -> ObservableSet[State]:
        return self._final_states
    
    @final_states.setter
    def final_states(self, value: Set[State]) -> None:        
        self._final_states = self._final_states_from_set(value)
    
    @property
    def alphabet(self) -> ObservableSet[str]:
        return self._alphabet
    
    @alphabet.setter
    def alphabet(self, value: Set[str]) -> None:
        for start_state, letter in list(self.transition_table.keys()):
            if letter not in value:
                del self.transition_table[(start_state, letter)]
        
        self._alphabet = self._alphabet_from_set(value)
    
    @property
    def transition_table(self) -> TransitionTable:
        return self._transition_table
    
    @property
    def is_dfa(self) -> bool:
        """Return a boolean flag indicating whether the FSA is a 
        deterministic FSA (DFA) or not."""
        return all(
            label != EPSILON
            and len(self.delta(state, label)) <= 1
            for state, label in self.transition_table.keys()
        )
    
    @property
    def is_complete_dfa(self) -> bool:
        """Return a boolean flag indicating whether the FSA is a 
        complete DFA.

        A complete DFA must have exactly 1 outgoing transition for 
        every combination of state and letter.
        """
        return self.is_dfa and all(
            len(self.delta(state, letter)) == 1
            for letter in self.alphabet
            for state in self.states
        )

    @property
    def is_nfa(self) -> bool:
        """Return a boolean flag indicating whether the FSA is a 
        non-deterministic FSA (NFA) or not."""
        return not self.is_dfa

    @property
    def is_epsilon_nfa(self) -> bool:
        """Return a boolean flag indicating whether the FSA is an 
        epsilon-NFA or not."""
        return self.is_nfa and any(
            label == EPSILON
            for _, label in self.transition_table.keys()
        )

    @property
    def type(self) -> str:
        """Get a string description of the type of the FSA."""
        if self.is_complete_dfa: return "Complete DFA"
        if self.is_dfa: return "DFA"
        if self.is_epsilon_nfa: return "Epsilon-NFA"

        return "NFA"

    def delta(self, state: State, label: str) -> frozenset[State]:        
        return frozenset(self.transition_table[(state, label)])

    def accepts(self, word: str) -> bool:
        """Return True if the FSA accepts the given word otherwise 
        False."""
        return FSA._dfa_accepts(subset_construction(self), word)

    def recognizes_empty_language(self) -> bool:
        """Return True if the FSA recognzies the empty language (a set 
        with no words), otherwise False.
        """ 
        visited: set[State] = {self.initial_state}
        queue: deque[State] = deque([self.initial_state])

        while queue:
            current_state: State = queue.popleft()
            
            if current_state in self.final_states:
                return False
            
            for (start_state, _), end_states in (
                self.transition_table.items()
            ):
                if start_state == current_state:
                    for next_state in end_states:
                        if next_state not in visited:
                            visited.add(next_state)
                            queue.append(next_state)
                            
        return True

    def recognizes(self, language: set[str]) -> bool:
        """Return True if the FSA recognizes the given language, 
        otherwise False."""
        if not language: return self.recognizes_empty_language()

        dfa: FSA = subset_construction(self)

        return all(FSA._dfa_accepts(dfa, word) for word in language)
    
    @staticmethod
    def _dfa_accepts(dfa: FSA, word: str) -> bool:
        """Return True if the given DFA accepts the given word, 
        otherwise False.

        Raises:
            ValueError: If the given FSA is not a DFA.
        """
        if not dfa.is_dfa:
            raise ValueError(
                f"Expected a DFA. Got an FSA of type '{dfa.type}'."
            )

        current_state: State = dfa.initial_state

        for letter in word:
            next_states: frozenset[State] = dfa.delta(current_state, letter)

            # no next state so we hit a dead-end which means the word 
            # is not accepted
            if not next_states: return False

            # since we are traversing a DFA the set only has one state
            (current_state, ) = next_states

        return current_state in dfa.final_states
    
    def _final_states_from_set(
        self, 
        final_states: Set[State] | None = None
    ) -> ObservableSet[State]:
        return ObservableSet[State](
            final_states,
            pre_discard=lambda state: self.states.discard(state),
            pre_add=lambda state: hooks.final_states.pre_add(
                state=state, 
                possible_states=self.states
            )
        )
    
    def _states_from_set(
        self,
        states: Set[State]
    ) -> ObservableSet[State]:
        return ObservableSet[State](
            states,
            pre_add=lambda state: hooks.states.pre_add(state, self.states),
            pre_discard=lambda state: hooks.states.pre_discard(
                state=state,
                states=self.states,
                initial_state=self.initial_state,
                final_states=self.final_states,
                transition_table=self.transition_table
            )
        )
    
    def _alphabet_from_set(
        self,
        alphabet: Set[str] | None = None
    ) -> ObservableSet[str]:
        return ObservableSet[str](
            alphabet,
            pre_add=lambda letter: hooks.alphabet.pre_add(letter),
            pre_discard=lambda letter: hooks.alphabet.pre_discard(
                letter=letter, 
                transition_table=self.transition_table
            ),
        )
    
    def _transition_table_from_set(
        self,
        transitions: Set[State, str, State] | None = None
    ) -> TransitionTable:
        return TransitionTable(
            (
                {
                    (start_state, label): end_state
                    for start_state, label, end_state
                    in transitions
                }
                if transitions is not None
                else None
            ),
            pre_setitem=(
                lambda key, value: hooks.transition_table.pre_setitem(
                    key=key,
                    value=value,
                    states=self.states,
                    alphabet=self.alphabet
                )
            ),
            pre_value_add=lambda state: hooks.transition_table.pre_value_add(
                state=state,
                possible_states=self.states
            ),
        )