class NamedObject:
    """Represents an object with a name."""

    # the object's name
    _name: str

    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.name}')"
