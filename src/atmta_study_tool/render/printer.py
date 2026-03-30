from collections.abc import Iterable, Set
from os import PathLike
from ._renderer import Renderer
from pathlib import Path


class Printer(Renderer):
    """Represents a printer that prints content to stdout or a file."""

    # output directory where file-based prints should go
    _PRINT_FILE_DIR: Path = Renderer._RENDER_DIR / "txt"

    def _get_set_str(self, items: Set[object]) -> str:
        """Get a string representing the given items as a set."""
        return "{" + ", ".join(str(item) for item in items) + "}"

    def _get_tuple_str(self, items: Iterable[object]) -> str:
        """Get a string representing the given items as a tuple."""
        return "(" + ", ".join(str(item) for item in items) + ")"

    def print(self, content: str, filename: PathLike | str | None = None):
        """Print the given string content to the given file or stdout if None given."""
        if filename is None:
            print(content)
        else:
            path: Path = self._PRINT_FILE_DIR / Path(filename).with_suffix(".txt")

            with open(path, mode="w") as f:
                print(content, file=f)
