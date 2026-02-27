from __future__ import annotations
from collections import deque, defaultdict
from typing import AbstractSet
from .state import State
from .word import EPSILON
from .transition_table import TransitionTable
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
        states: AbstractSet[State],
        alphabet: AbstractSet[str] | None = None,
        transitions: AbstractSet[tuple[State, str, State]] | None = None,
        final_states: AbstractSet[State] | None = None
    ):
        self._initial_state = initial_state

        hooks.states.pre_set(
            new_states=states, 
            current_initial_state=self.initial_state
        )

        states_processed: set[State] = set()

        self._states = ObservableSet[State](
            states,
            pre_add=lambda state: hooks.states.pre_add(
                new_state=state,
                current_states=states_processed
            ),
            post_add=lambda state: states_processed.add(state),
            pre_discard=lambda state: hooks.states.pre_discard(
                state=state,
                current_states=self.states,
                current_initial_state=self.initial_state,
                current_final_states=self.final_states,
                current_transition_table=self.transition_table
            )
        )

        self._states._post_add = None
        self._states._pre_add = lambda state: hooks.states.pre_add(
            new_state=state,
            current_states=self.states
        )

        self._alphabet = self._alphabet_from_set(alphabet)
        self._final_states = self._final_states_from_set(final_states)
        self._transition_table = self._transition_table_from_set(transitions)

    @property
    def states(self) -> ObservableSet[State]:
        """Get the FSA's set of states."""
        return self._states
    
    @states.setter
    def states(self, value: AbstractSet[State]) -> None:
        hooks.states.pre_set(
            new_states=value, 
            current_initial_state=self.initial_state
        )
        
        self._states = ObservableSet[State](
            value,
            pre_add=lambda state: hooks.states.pre_add(
                new_state=state, 
                current_states=self.states
            ),
            pre_discard=lambda state: hooks.states.pre_discard(
                state=state,
                current_states=self.states,
                current_initial_state=self.initial_state,
                current_final_states=self.final_states,
                current_transition_table=self.transition_table
            )
        )
    
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
    def final_states(self, value: AbstractSet[State]) -> None:        
        self._final_states = self._final_states_from_set(value)
    
    @property
    def alphabet(self) -> ObservableSet[str]:
        return self._alphabet
    
    @alphabet.setter
    def alphabet(self, value: AbstractSet[str]) -> None:
        for start_state, letter in list(self.transition_table.keys()):
            if letter not in value:
                del self.transition_table[(start_state, letter)]
        
        self._alphabet = self._alphabet_from_set(value)
    
    @property
    def transition_table(self) -> TransitionTable:
        return self._transition_table
    
    @transition_table.setter
    def transition_table(self, value: AbstractSet[tuple[State, str, State]]) -> None:
        self._transition_table = self._transition_table_from_set(value)
    
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
        return FSA._dfa_accepts(self.subset_construction(), word)

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

        dfa: FSA = self.subset_construction()

        return all(FSA._dfa_accepts(dfa, word) for word in language)
    
    def epsilon_removal(self) -> FSA:
        nfa: FSA = FSA(
            initial_state=self.initial_state,
            states={self.initial_state},
            alphabet=set(self.alphabet)
        )

        e_closures: dict[State, frozenset[State]] = {
            state: self.epsilon_closure({state})
            for state in self.states
        }

        # step 2: iterate over the states
        for state in self.states:
            # step 2.1: get the epsilon closure of the state
            state_e_closure: frozenset[State] = e_closures[state]

            # step 3: iterate over the states and alphabet
            for letter in self.alphabet:
                # step 3.1: calculate the end states and the new FSA's 
                # transition table
                # formula: 
                # d'(state, letter) = ECLOSE(d(ECLOSE(state), letter))
                end_states: set[State] = {
                    destination
                    for closure_state in state_e_closure
                    for transition_state in self.delta(closure_state, letter)
                    for destination in e_closures[transition_state]
                }

                if end_states:
                    nfa.transition_table[(state, letter)] = end_states

            if any(
                closure_state in self.final_states 
                for closure_state in state_e_closure
            ): nfa.final_states.add(state)
        
        return nfa
        
    def epsilon_closure(self, states: AbstractSet[State]) -> frozenset[State]:
        """Get the epsilon-closure of a set of states in the FSA.

        Args:
            states: The set of starting stats from which to start considering 
            epsilon transitions.

        Returns:
            set[State]: The epsilon-closure which contains all states 
            that can be reached by only following epsilon-transitions 
            from the given states. At minimum this will be a set states 
            including all the given states.
        """
        closure: set[State] = set(states)
        queue: deque[State] = deque(states)

        while queue:
            current_state: State = queue.popleft()
            next_states: frozenset[State] = self.delta(current_state, EPSILON)

            for state in next_states:
                if state not in closure:
                    closure.add(state)
                    queue.append(state)

        return frozenset(closure)
    
    def subset_construction(self) -> FSA:
        """Construct an equivalent deterministic FSA from the current 
        FSA via the subset construction algorithm.

        If the FSA is not deterministic, the implementation will always 
        produce a complete DFA.

        Returns:
            FSA: An equivalent deterministic FSA or a reference to the 
            FSA itself if already deterministic.
        """
        # step 1: get the DFA's initial state (NFA epsilon closure)
        dfa_initial_state: frozenset[State] = self.epsilon_closure(
            {self.initial_state}
        )

        seen_states: dict[frozenset[State], State] = {
            dfa_initial_state: State(dfa_initial_state)
        }

        dfa: FSA = FSA(
            initial_state=seen_states[dfa_initial_state],
            states={seen_states[dfa_initial_state]},
            alphabet=set(self.alphabet),
        )

        # step 2: discover all DFA states and construct the DFA 
        # transition table 
        discovered_states: deque[frozenset[State]] = deque(
            [dfa_initial_state]
        )

        while discovered_states:
            current_dfa_state: frozenset[State] = discovered_states.popleft()

            for letter in self.alphabet:
                # step 2.1: find all reachable states in the NFA from 
                # the set of NFA states in the current DFA states;
                # this becomes the next DFA state
                # union of epsilon closures of the delta
                next_dfa_state: frozenset[State] = frozenset({
                    state
                    for start_nfa_state in current_dfa_state
                    for state in self.epsilon_closure(
                        self.delta(start_nfa_state, letter)
                    )
                })

                # step 2.2: put the transition in the transition table
                # if nothing is reachable, then we will point the 
                # transition to the dummy state (represented by the 
                # empty set here)
                if next_dfa_state not in seen_states:
                    seen_states[next_dfa_state] = State(next_dfa_state)
                    dfa.states.add(seen_states[next_dfa_state])
                    discovered_states.append(next_dfa_state)

                dfa.transition_table[
                    (seen_states[current_dfa_state], letter)
                ] = {seen_states[next_dfa_state]}

        dfa.final_states = {
            dfa_state
            for nfa_states, dfa_state in seen_states.items()
            if any(
                nfa_state in self.final_states
                for nfa_state in nfa_states
            )
        }

        return dfa
    
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
        final_states: AbstractSet[State] | None = None
    ) -> ObservableSet[State]:
        return ObservableSet[State](
            final_states,
            pre_discard=lambda state: self.states.discard(state),
            pre_add=lambda state: hooks.final_states.pre_add(
                new_final_state=state, 
                current_states=self.states
            )
        )
    
    def _alphabet_from_set(
        self,
        alphabet: AbstractSet[str] | None = None
    ) -> ObservableSet[str]:
        return ObservableSet[str](
            alphabet,
            pre_add=lambda letter: hooks.alphabet.pre_add(letter),
            pre_discard=lambda letter: hooks.alphabet.pre_discard(
                letter=letter, 
                current_transition_table=self.transition_table
            ),
        )
    
    def _transition_table_from_set(
        self,
        transitions: AbstractSet[tuple[State, str, State]] | None = None
    ) -> TransitionTable:
        transition_data: defaultdict[tuple[State, str], set[State]] | None

        if transitions is not None:
            transition_data = defaultdict(set)

            for start_state, label, end_state in transitions:
                transition_data[(start_state, label)].add(end_state)
        else: transition_data = None

        return TransitionTable(
            transition_data,
            pre_setitem=(
                lambda key, value: hooks.transition_table.pre_setitem(
                    key=key,
                    value=value,
                    current_states=self.states,
                    current_alphabet=self.alphabet
                )
            ),
            pre_value_add=lambda state: hooks.transition_table.pre_value_add(
                new_state=state,
                current_states=self.states
            ),
        )