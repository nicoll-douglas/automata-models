from ..types import SymbolLike
from ..models.symbol import Symbol
from collections.abc import Iterable, Iterator


def symbol_from(symbol_like: SymbolLike) -> Symbol:
    """Create and return a symbol from a symbol-like.

    If a symbol is passed then it is returned.
    """
    return Symbol(symbol_like) if isinstance(symbol_like, str) else symbol_like


def symbols_from(symbol_likes: Iterable[SymbolLike]) -> Iterator[Symbol]:
    """Create and yield symbols from symbol-likes.

    If a symbol is encountered then it is yielded.
    """
    for symbol_like in symbol_likes:
        yield symbol_from(symbol_like)
