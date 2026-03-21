from collections import UserList
from .symbol import Symbol


class Word(UserList[Symbol]):
    """Implements a word as a list of symbols."""

    pass


class Epsilon:
    """Singleton class that returns the empty word when instantiated."""

    _instance: Word | None

    def __new__(cls, *args, **kwargs) -> Word:
        if cls._instance is None:
            cls._instance = Word()

        return cls._instance
