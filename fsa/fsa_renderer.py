from __future__ import annotations
from graphviz import Digraph
from .word import EPSILON

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .fsa import FSA

class FSARenderer:
    """Represents a renderer object that can render FSA diagrams."""

    # the label used for epsilon-transitions
    EPSILON_LABEL: str = "\u03b5"

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
            shape: str = (
                "doublecircle" 
                if state in fsa.final_states 
                else "circle"
            )

            graph.node(state.label, shape=shape)

        for (start_state, label), end_states in (
            fsa.transition_table.items()
        ):
            diagram_label: str = (
                FSARenderer.EPSILON_LABEL
                if label == EPSILON 
                else label
            )

            for end_state in end_states:
                graph.edge(
                    start_state.label, 
                    end_state.label,
                    label=diagram_label
                )

        graph.node("start", label="", shape="none", width="0", height="0")
        graph.edge("start", fsa.initial_state.label)
        graph.render(filename, view=open_file, cleanup=True)