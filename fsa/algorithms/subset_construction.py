from ..models.fsa import FSA
from ..models.state import State
from collections import deque
from copy import deepcopy
from typing import AbstractSet, TYPE_CHECKING

if TYPE_CHECKING:
    from language.models import Symbol


class _NewDFAState:
    """Represents a state in the new DFA being computed via subset construction."""

    # the set of FSA states in the old FSA that comprise the new DFA state
    _states: frozenset[State]
    # the actual state object that will be given to the new DFA
    _state_obj: State

    def __init__(self, states: AbstractSet[State]):
        self._states = frozenset(states)
        # sorting here means each state object produced from the same set of states will be equivalent as they will have the same UID
        state_obj_uid: str = "{" + ", ".join(sorted(str(s) for s in states)) + "}"
        self._state_obj = State(state_obj_uid)

    @property
    def state_obj(self) -> State:
        return self._state_obj

    @property
    def states(self) -> frozenset[State]:
        return self._states


def _get_new_dfa_initial_state(old_fsa: FSA) -> _NewDFAState:
    """Compute the initial state of the new DFA.

    Uses the formula: q_0' = E({q_0})

    Args:
        old_fsa: The old FSA from which we are constructing a new DFA.
    """
    return _NewDFAState(old_fsa.epsilon_closure(old_fsa.initial_state))


def _is_new_dfa_final_state(
    new_dfa_state: _NewDFAState, old_fsa_final_states: AbstractSet[State]
) -> bool:
    """Return True if given new DFA state is a final state, otherwise False.

    Uses the formula: S ∩ F != Ø, where S is a a new DFA state and F is the old set of final states. I.e, the new final state contains an old final state.

    Args:
        new_dfa_state: A new state in the DFA.
        old_fsa_final_states: The final states of the old FSA from which we are creating a DFA.
    """
    return len(new_dfa_state & old_fsa_final_states) != 0


def _get_new_dfa_delta(
    dfa_start_state: _NewDFAState, symbol: Symbol, old_fsa: FSA
) -> _NewDFAState:
    """Get a the transition state for a starting state and symbol in the new DFA.

    Uses the formula: δ'(S, a) = ∪(s∈S) E(δ(s, a)), where S is a state in the new DFA and 'a' is the transition symbol.

    Args:
        dfa_state_state: The starting state of the transition.
        symbol: The transition symbol.
        old_fsa: The old FSA from which we are computing a new DFA.
    """
    next_state: set[State] = set()

    for old_fsa_state in dfa_start_state.states:
        next_state |= old_fsa.epsilon_closure(old_fsa.delta(old_fsa_state, symbol))

    return _NewDFAState(next_state)


def subset_construction(fsa: FSA, complete: bool = True) -> FSA:
    """Construct an equivalent DFA from the given FSA via the subset construction algorithm.

    Args:
        complete: Whether the resulting DFA should be a complete DFA.

    Returns:
        An equivalent DFA.
    """
    # get the DFA's initial state (NFA epsilon closure)
    dfa_initial_state: _NewDFAState = _get_new_dfa_initial_state(fsa)

    dfa: FSA = FSA(
        initial_state=dfa_initial_state.state_obj,
        states={dfa_initial_state.state_obj},
        final_states=(
            {dfa_initial_state.state_obj}
            if _is_new_dfa_final_state(dfa_initial_state)
            else None
        ),
        alphabet=deepcopy(fsa.alphabet),
    )

    states_unprocessed: deque[_NewDFAState] = deque([dfa_initial_state])

    # discover all DFA states and construct the DFA transition table
    while states_unprocessed:
        current_dfa_state: _NewDFAState = states_unprocessed.popleft()

        for symbol in fsa.alphabet:
            # get the delta
            discovered_state: _NewDFAState = _get_new_dfa_delta(
                current_dfa_state, symbol, fsa
            )

            if not complete and not discovered_state:
                continue

            # check if the state hasn't already been discovered
            if discovered_state.state_obj not in dfa.states:
                dfa.states.add(discovered_state.state_obj)

                # check whether this new discovered state is final and add it if so
                if _is_new_dfa_final_state(discovered_state):
                    dfa.final_states.add(discovered_state.state_obj)

                # add the new discovered state for processing
                states_unprocessed.append(discovered_state)

            # add the transition to the transition table
            dfa.transition_table[(current_dfa_state.state_obj, symbol)] = {
                discovered_state.state_obj
            }

    return dfa
