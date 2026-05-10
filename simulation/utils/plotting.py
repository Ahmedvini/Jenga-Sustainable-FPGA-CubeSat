"""Optional plotting helpers."""

from pathlib import Path


def write_placeholder(path: Path, title: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{title}\nGenerated graph placeholder.\n", encoding="utf-8")
