from enum import IntFlag, auto

class FSAType(IntFlag):
    DFA = auto()
    COMPLETE_DFA = auto()
    NFA = auto()
    EPSILON_NFA = auto()
    