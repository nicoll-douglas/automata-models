class UID[T]:
    """Represents a unique identifier (UID).

    Two UID objects are equal if and only if they have equal 'uid' attributes and are of the same type.
    """

    uid: T

    def __init__(self, uid: T):
        self.uid = uid

    def __eq__(self, other: object) -> bool:
        if type(other) is self.__class__:
            return self.uid == other.uid

        return False

    def __hash__(self) -> int:
        return hash(self.uid)

    def __str__(self) -> str:
        return str(self.uid)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.uid!r}')"
