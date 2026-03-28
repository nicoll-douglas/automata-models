from atmta_study_tool._common.data_structures import ObservableSet
from .symbol import Symbol
from collections.abc import Iterable
from ..types import SymbolLike
from ..utils import symbols_from


class Alphabet(ObservableSet[Symbol]):
    """Implements an alphabet as an observable set of symbols."""

    def __init__(
        self,
        symbols: Iterable[SymbolLike] | None = None,
    ):
        if symbols is None:
            super().__init__()

            return

        super().__init__(symbols_from(symbols))
