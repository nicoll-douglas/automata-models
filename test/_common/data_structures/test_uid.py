from _common.data_structures.uid import UID
from typing import Any


class TestUID:
    def test_interning(self):
        """Test that the UID class correctly interns two equivalent UID objects.

        Arrange: Create a UID object.
        Act: Create an equivalent UID object to the first.
        Assert: Check that both UID objects are the same object and that they are one interned value.
        """
        uid_str: str = "abcd"
        uid_a: UID[str] = UID(uid_str)
        registry_key: tuple[type[UID[Any]], str] = (UID, uid_str)

        # assert uid_a gets interned
        assert registry_key in UID._REGISTRY
        assert uid_a is UID._REGISTRY[registry_key]

        uid_b: UID[str] = UID(uid_str)

        # assert uid_b with the same uid_str is the interned value
        assert uid_b is uid_a
        assert uid_b is UID._REGISTRY[registry_key]

        # assert that only one 1 interned value was created
        assert len(UID._REGISTRY) == 1
