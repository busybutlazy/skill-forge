from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
import tomllib

__all__ = ["__version__"]


def _project_version() -> str:
    # Prefer the source of truth when running from a checkout or runtime image.
    pyproject = Path(__file__).resolve().parents[2] / "pyproject.toml"
    if pyproject.is_file():
        with pyproject.open("rb") as stream:
            return str(tomllib.load(stream)["project"]["version"])

    try:
        return version("skill-forge")
    except PackageNotFoundError:
        return "unknown"


__version__ = _project_version()
