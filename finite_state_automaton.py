from __future__ import annotations
from collections import defaultdict, deque
from collections.abc import Set
from graphviz import Digraph
from typing import Generic
import pprint

class FSA:
    type Alphabet = set[str]
    type Transition = tuple[State, str, State]
    type TransitionTable = defaultdict[tuple[State, str], set[State]]
    type DFASetTransitionTable = dict[tuple[frozenset[State], str], frozenset[State]]

    _transitions: set[Transition]
    _alphabet: Alphabet
    _states: set[State]
    _initial_state: State
    _final_states: set[State]

    def __init__(
        self,
        transitions: set[Transition],
        alphabet: Alphabet,
        states: set[State],
        initial_state: State,
        final_states: set[State]
    ):
        # independent variables, no validation needed
        self._initial_state = initial_state
        self._alphabet = alphabet

        error_msg: str | None = self._validate_states(states)

        if error_msg is not None: raise ValueError(error_msg)

        self._states = states
        self.final_states = final_states
        self.transitions = transitions

    class State:
        label: str

        def __init__(self, label: str | Set[FSA.State]):
            if isinstance(label, str):
                self.label = label
            else:
                self.label = "{" + ", ".join(state.label for state in label) + "}"

    @property
    def states(self) -> set[State]:
        return self._states

    @states.setter
    def states(self, incoming_states: set[State]) -> None:
        """Set the states of the automaton.

        As a side effect, the method removes any final states not in the new set of states to preserve integrity.
        
        Raises:
            ValueError: If the set of new states does not contain the current initial state or if the given labels for the new states are not unique
        """
        error_msg: str | None = self._validate_states(incoming_states)

        if error_msg is not None: raise ValueError(error_msg)
        
        self.final_states -= incoming_states # remove any final states that will no longer exist
        self.transitions -= {
            (start_state, letter, end_state)
            for start_state, letter, end_state in self.transitions
            if start_state not in incoming_states
            or end_state not in incoming_states
        } # remove any transitions for states that will no longer exist
        self._states = incoming_states

    @property
    def initial_state(self) -> State:
        return self._initial_state

    @initial_state.setter
    def initial_state(self, new_initial: State) -> None:
        if new_initial not in self.states:
            raise ValueError("The initial state must be in the set of states")

        self._initial_state = new_initial

    @property
    def final_states(self) -> set[State]:
        return self._final_states

    @final_states.setter
    def final_states(self, incoming_final_states: set[State]) -> None:
        """Set the automaton's final states.

        Raises:
            ValueError: If any new final state is not in the current set of states.
        """
        if not incoming_final_states <= self.states:
            raise ValueError("All final states must be in the set of states")

        self._final_states = incoming_final_states
    
    @property
    def alphabet(self) -> Alphabet:
        return self._alphabet

    @alphabet.setter
    def alphabet(self, incoming_alphabet: Alphabet) -> None:
        """Set the alphabet of the automaton.

        As a side effect, the method removes transitions from the automaton where a transition's letter is not in the new alphabet to preserve integrity.
        """
        self.transitions -= {
            (start_state, letter, end_state)
            for start_state, letter, end_state in self.transitions
            if letter not in incoming_alphabet
        } # remove any transitions with letters that will no longer exist

        self._alphabet = incoming_alphabet

    @property
    def transitions(self) -> set[Transition]:
        return self._transitions

    @transitions.setter
    def transitions(self, incoming_transitions: set[Transition]) -> None:
        """Set the transitions of the automaton.

        Raises:
            ValueError: If there is at least 1 incoming transition such that its start or end states are not in the current set of states or its letter is not in the current alphabet.
        """
        if any(
            start_state not in self.states
            or end_state not in self.states
            or letter not in self.alphabet
            for start_state, letter, end_state in incoming_transitions
        ): raise ValueError("All transition states must be in the set of states and all transition letters must be in the alphabet")
    
        self._transitions = incoming_transitions
   
    @property
    def deterministic(self) -> bool:
        return all(len(end_states) <= 1 for end_states in self.transition_table.values()) 

    @property
    def transition_table(self) -> TransitionTable:
        al: FSA.TransitionTable = defaultdict(set) 

        for start_state, letter, end_state in self.transitions:
            al[(start_state, letter)].add(end_state)

        return al 

    def epsilon_closure(self, starting_state: State) -> set[State]:
        if starting_state not in self.states: raise ValueError("Starting state must be in the set of states to find the epsilon-closure")

        transition_table: FSA.TransitionTable = self.transition_table
        closure: set[FSA.State] = {starting_state}
        queue: deque[FSA.State] = deque([starting_state])

        while queue:
            current: FSA.State = queue.popleft()
            next_states: set[FSA.State] = transition_table[(current, "")]

            for state in next_states:
                if state not in closure:
                    closure.add(state)
                    queue.append(state)

        return closure 

    def subset_construction(self) -> FSA:
        if self.deterministic: return self

        # step 1: get the NFA transition table and DFA initial state (NFA epsilon closure)
        nfa_transition_table: FSA.TransitionTable = self.transition_table
        dfa_initial_state: frozenset[FSA.State] = frozenset(self.epsilon_closure(self.initial_state))

        # step 2: discover all DFA states and construct the DFA transition table 
        queue: deque[frozenset[FSA.State]] = deque([dfa_initial_state])
        dfa_states: set[frozenset[FSA.State]] = {dfa_initial_state}
        dfa_transition_table: FSA.DFASetTransitionTable = {}

        while queue:
            current_dfa_state: frozenset[FSA.State] = queue.popleft()

            for letter in self.alphabet:
                # step 2.1: find all reachable states in the NFA from the set of NFA states in the current DFA states
                reachable_states: frozenset[FSA.State] = set()

                for nfa_state in current_dfa_state:
                    for transition_state in nfa_transition_table[(nfa_state, letter)]:
                        reachable_states.update(self.epsilon_closure(transition_state))

                # step 2.2: construct the next DFA state from the reachables
                next_dfa_state: frozenset[FSA.State] = frozenset(reachable_states)

                # if nothing is reachable, then we will point the transition to the dummy state (represented by the empty set here)
                dfa_transition_table[(current_dfa_state, letter)] = next_dfa_state

                if next_dfa_state not in dfa_states:
                    dfa_states.add(next_dfa_state) 
                    queue.append(next_dfa_state)
        
        # step 3: construct the new automaton and identify the DFA final states
        dfa_state_map: dict[frozenset[FSA.State], FSA.State] = {
            dfa_state: self.State(dfa_state)
            for dfa_state in dfa_states
        }

        return FSA(
            alphabet=self.alphabet.copy(),
            initial_state=dfa_state_map[dfa_initial_state],
            final_states={
                dfa_state_map[dfa_state]
                for dfa_state in dfa_states
                if any(nfa_state in self.final_states for nfa_state in dfa_state)
            },
            states=set(dfa_state_map.values()),
            transitions={
                (dfa_state_map[start_state], letter, dfa_state_map[end_state])
                for (start_state, letter), end_state in dfa_transition_table.items()
            }
        )
       
    def _validate_states(self, states: set[State]) -> str | None:
        """Validate whether the given set of states is a valid assignment for the automaton's states.

        Returns:
            None | str: None if validation passed or an error message if validation failed.
        
        Raises:
            ValueError: If the set of new states does not contain the current initial state or if the given labels for the new states are not unique
        """
        if self.initial_state not in states:
            return "The initial state must be in the set of states"

        if len([state.label for state in states]) != len({state.label for state in states}):
            return "All states must have unique labels"
        
        return None


    def draw(self, filename: str, open_file: bool = True) -> None:
        graph: Digraph = Digraph("FSA", format="png")

        graph.attr(rankdir="LR")

        for state in self.states:
            shape: str = "doublecircle" if state in self.final_states else "circle"

            graph.node(state.label, shape=shape)

        for start_state, letter, end_state in self.transitions:
            graph.edge(start_state.label, end_state.label, label=letter)

        graph.node("start", label="", shape="none", width="0", height="0")
        graph.edge("start", self.initial_state.label)

        graph.render(filename, view=open_file)




q0: FSA.State = FSA.State("q0")
q1: FSA.State = FSA.State("q1")

fsa: FSA = FSA(
    states={q0, q1},
    initial_state=q0,
    final_states=set(),
    alphabet={"a", "b"},
    transitions={
        (q0, "a", q1),
    }
)

fsa.subset_construction().draw("fsa_output_2")
