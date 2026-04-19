from pathlib import Path


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def ensure_directory(path: str | Path) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory