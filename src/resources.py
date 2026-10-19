import os
import sys


def resource_path(relative_path: str) -> str:
    """Resolve the absolute path to a resource/asset file.

    Uses PyInstaller's temporary extraction directory when running from the
    bundled executable, otherwise the project root during development.

    Args:
        relative_path: Path relative to the project root (e.g. 'img/logo.png').

    Returns:
        The absolute file system path to the requested asset.
    """
    base_path = getattr(
        sys,
        "_MEIPASS",
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    )

    return os.path.join(base_path, relative_path)
