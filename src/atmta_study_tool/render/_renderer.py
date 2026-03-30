from pathlib import Path
from abc import ABC


class Renderer(ABC):
    """Represents a base renderer object."""

    # the path where any file-based renders should go
    _RENDER_DIR: Path = Path("renders")
