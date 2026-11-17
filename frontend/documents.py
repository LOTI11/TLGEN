"""Document discovery helpers (filesystem listing only, no parsing)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from frontend.config import SUPPORTED_EXTENSIONS


@dataclass(frozen=True)
class DocumentRef:
    """A document chosen from the repository directory or uploaded by the user."""

    name: str
    source: str  # "repository" | "upload"
    size_bytes: int
    path: Path | None = None  # set for repository documents


def format_size(size_bytes: int) -> str:
    size = float(size_bytes)
    for unit in ("B", "KB", "MB"):
        if size < 1024:
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} GB"


def list_available_documents(directory: Path) -> list[DocumentRef]:
    """Return supported files found directly inside ``directory`` (non-recursive)."""
    if not directory.is_dir():
        return []
    suffixes = {f".{ext}" for ext in SUPPORTED_EXTENSIONS}
    return [
        DocumentRef(p.name, "repository", p.stat().st_size, p)
        for p in sorted(directory.iterdir(), key=lambda p: p.name.lower())
        if p.is_file() and p.suffix.lower() in suffixes
    ]
