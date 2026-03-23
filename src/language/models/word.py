from __future__ import annotations
from .symbol import Symbol
from typing import override


class Word(tuple[Symbol]):
    """Implements a word as a list of symbols."""

    # the empty word
    EPSILON: Word

    def __repr__(self):
        return f"{self.__class__.__name__}({super().__repr__()})"
    
    @override
    def __add__(self, other):
        return Word(super().__add__(other))
    
    @override
    def __mul__(self, other):
        return Word(super().__mul__(other))
    
    @override
    def __getitem__(self, index: int | slice) -> Symbol | Word:
        item: Symbol | tuple[Symbol, ...] = super().__getitem__(index)

        if isinstance(index, slice):
            return Word(item)

        return item


Word.EPSILON = Word()
