from __future__ import annotations
from graphviz import Digraph
from collections import defaultdict
from .word import EPSILON

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .fsa import FSA
    from .state import State

class FSARenderer:
    """Represents a renderer object that can render FSA diagrams."""

    # the label used for epsilon-transitions
    EPSILON_LABEL: str = "\u03b5"

    combine_edges: bool

    def __init__(self, combine_edges: bool = True):
        self.combine_edges = combine_edges

    def render(self, fsa: FSA, filename: str, open_file: bool = True) -> None:
        """Create an image representation of the given FSA and optionally 
        open the image file.

        Args:
            filename: The extension-less filename to give the .png file.
            open_file: Whether to open the .png file for immediate 
            viewing.
        """
        graph: Digraph = Digraph("FSA", format="png")

        graph.attr(rankdir="LR")

        for state in fsa.states:
            graph.node(state.label, shape=(
                "doublecircle" 
                if state in fsa.final_states 
                else "circle"
            ))

        state_pairs: defaultdict[
            tuple[State, State], 
            set[str]
        ] = defaultdict(set)

        for (start_state, label), end_states in (
            fsa.transition_table.items()
        ):
            diagram_label: str = (
                FSARenderer.EPSILON_LABEL
                if label == EPSILON 
                else label
            )
            if self.combine_edges:
                for end_state in end_states:
                    state_pairs[(start_state, end_state)].add(diagram_label)
            else:
                for end_state in end_states:
                    graph.edge(
                        start_state.label, 
                        end_state.label,
                        label=diagram_label
                    )
        
        if self.combine_edges:
            for (start_state, end_state), labels in state_pairs.items():
                graph.edge(
                    start_state.label,
                    end_state.label,
                    label=", ".join(sorted(list(labels)))
                )

        graph.node("start", label="", shape="none", width="0", height="0")
        graph.edge("start", fsa.initial_state.label)
        graph.render(filename, view=open_file, cleanup=True)