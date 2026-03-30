from .printer import Printer
from .transition_graph_renderer import TransitionGraphRenderer
from atmta_study_tool.fsa import FSA, EpsilonFSA


class FSARenderer(TransitionGraphRenderer[FSA | EpsilonFSA], Printer):
    """Represents a renderer object that can render FSAs."""

    def formal(self) -> str:
        """Return the FSA as its formal 5-tuple definition."""
        return self._get_tuple_str(
            [
                self._get_set_str(self.fsa.alphabet),
                self._get_set_str(self.fsa.states),
                self._get_set_str(
                    {
                        self._get_tuple_str(t)
                        for t in self.fsa.transition_table.flatten()
                    }
                ),
                self._get_set_str(self.fsa.final_states),
                str(self.fsa.initial_state),
                self._get_set_str(self.fsa.final_states),
            ]
        )
