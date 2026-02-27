from typing import AbstractSet

class State:
    """Represents a state in an FSA."""

    # the state's arbitrary label for diagrams
    _label: str 

    def __init__(self, label: str | AbstractSet[State]):
        self._label = (
            label 
            if isinstance(label, str)
            else (
                "{" + ", ".join(state.label for state in label) + "}"
            )
        )

    @property
    def label(self) -> str:
        return self._label

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.label}')"