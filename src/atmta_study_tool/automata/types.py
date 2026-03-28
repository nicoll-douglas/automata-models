from .models.state import State
from atmta_study_tool.language import Symbol, Word

# a "state-like" object i.e a State or the UID of a State
type StateLike = State | str

# a base transition in a transition table or automaton (a symbol or epsilon)
type Transition = Symbol | Word

# a "transition-like" object (a transition, or a symbol UID, or the epsilon UID)
type TransitionLike = Transition | str
