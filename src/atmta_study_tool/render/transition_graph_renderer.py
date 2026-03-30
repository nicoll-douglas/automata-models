from os import PathLike
from graphviz import Digraph
from collections import defaultdict
from atmta_study_tool.fsa import State, AbstractFSA
from ._image_renderer import ImageRenderer


class TransitionGraphRenderer[F: AbstractFSA](ImageRenderer):
    """Represents a transition graph image renderer for automata."""

    # whether to combine multiple transitions between two states into one edge
    combine_edges: bool
    # the FSA from which to build a transition graph
    fsa: F

    def __init__(self, fsa: F, combine_edges: bool = True) -> None:
        super().__init__()

        self.fsa = fsa
        self.combine_edges = combine_edges

    def _insert_nodes(self, graph: Digraph) -> None:
        """Insert nodes into the transition graph."""
        for state in self.fsa.states:
            graph.node(
                state.UID,
                shape=("doublecircle" if state in self.fsa.final_states else "circle"),
            )

    def _insert_edges(self, graph: Digraph) -> None:
        """Insert edges into the transition graph."""
        for (start_state, symbol), next_states in self.fsa.transition_table.items():
            for next_state in next_states:
                graph.edge(
                    start_state.UID,
                    next_state.UID,
                    label=str(symbol),
                )

    def _insert_combined_edges(self, graph: Digraph) -> None:
        """Insert edges with combined transitions into the transition graph."""
        transition_labels: defaultdict[tuple[State, State], set[str]] = defaultdict(set)

        for (start_state, symbol), next_states in self.fsa.transition_table.items():
            for next_state in next_states:
                transition_labels[(start_state, next_state)].add(str(symbol))

        for (start_state, next_state), labels in transition_labels.items():
            graph.edge(start_state.UID, next_state.UID, label=", ".join(sorted(labels)))

    def _insert_initial_state_arrow(self, graph: Digraph) -> None:
        """Insert the arrow that points to the node of the initial state into the transition graph."""
        graph.node("start", label="", shape="none", width="0", height="0")
        graph.edge("start", self.fsa.initial_state.UID)

    def image(
        self,
        filename: PathLike | str,
        format: ImageRenderer.ImageFormat,
        view: bool = False,
    ) -> None:
        """Render an image representation of the transition graph and optionally open the image file.

        Args:
            filename: The filename to give the .png file.
            format: The format of the image file.
            view: Whether to open the image file for immediate viewing.
        """
        graph: Digraph = Digraph(format=format)

        graph.attr(rankdir="LR")
        self._insert_nodes(graph)

        if self.combine_edges:
            self._insert_combined_edges(graph)
        else:
            self._insert_edges(graph)

        self._insert_initial_state_arrow(graph)

        graph.render(
            filename,
            directory=self._IMAGE_RENDER_DIR,
            view=view,
            cleanup=True,
        )
