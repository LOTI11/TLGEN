"""Document discovery helpers (filesystem listing only, no parsing).

Two groups of documents are handled the same way: the user stories (``.md``,
required) and the UI designs exported from Figma (``.png``/``.pdf``, optional).
Each group has its own folder, extensions and session-state fields.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from frontend.config import DOCUMENTS_DIR, SUPPORTED_EXTENSIONS, UI_DOCUMENTS_DIR, UI_EXTENSIONS
from frontend.state import AppState


@dataclass(frozen=True)
class DocumentRef:
    """A document chosen from the repository directory or uploaded by the user."""

    name: str
    source: str  # "repository" | "upload"
    size_bytes: int
    path: Path | None = None  # set for repository documents


@dataclass(frozen=True)
class DocumentGroup:
    """One kind of input document: where it lives, its formats and its state fields."""

    key: str  # "stories" | "ui"; also the prefix of the widget keys
    extensions: tuple[str, ...]
    selected_attr: str  # AppState field: names selected from the repository folder
    uploaded_attr: str  # AppState field: uploaded files (name -> bytes)
    nonce_attr: str  # AppState field: resets the file uploader widget

    def directory(self) -> Path:
        # Looked up at call time so the folders can be changed (tests, env).
        return DOCUMENTS_DIR if self.key == "stories" else UI_DOCUMENTS_DIR

    def selected_names(self, state: AppState) -> set[str]:
        return getattr(state, self.selected_attr)

    def set_selected_names(self, state: AppState, names: set[str]) -> None:
        setattr(state, self.selected_attr, names)

    def uploaded(self, state: AppState) -> dict[str, bytes]:
        return getattr(state, self.uploaded_attr)


USER_STORIES = DocumentGroup(
    "stories", SUPPORTED_EXTENSIONS, "selected_repo_documents", "uploaded_documents", "uploader_nonce"
)
UI_DESIGNS = DocumentGroup(
    "ui", UI_EXTENSIONS, "selected_repo_ui", "uploaded_ui", "ui_uploader_nonce"
)


def format_size(size_bytes: int) -> str:
    size = float(size_bytes)
    for unit in ("B", "KB", "MB"):
        if size < 1024:
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} GB"


def list_available_documents(
    directory: Path, extensions: tuple[str, ...] = SUPPORTED_EXTENSIONS
) -> list[DocumentRef]:
    """Return supported files found directly inside ``directory`` (non-recursive)."""
    if not directory.is_dir():
        return []
    suffixes = {f".{ext}" for ext in extensions}
    return [
        DocumentRef(p.name, "repository", p.stat().st_size, p)
        for p in sorted(directory.iterdir(), key=lambda p: p.name.lower())
        if p.is_file() and p.suffix.lower() in suffixes
    ]


def list_group_documents(group: DocumentGroup) -> list[DocumentRef]:
    return list_available_documents(group.directory(), group.extensions)


def selected_documents(
    state: AppState,
    available: list[DocumentRef] | None = None,
    group: DocumentGroup = USER_STORIES,
) -> list[DocumentRef]:
    """Current selection of ``group`` (repository + uploaded), in display order.

    Pass ``available`` (from ``list_group_documents``) to avoid scanning
    the folder again when the caller already has the listing.
    """
    if available is None:
        available = list_group_documents(group)
    names = group.selected_names(state)
    repo = [d for d in available if d.name in names]
    uploaded = [
        DocumentRef(name, "upload", len(data)) for name, data in group.uploaded(state).items()
    ]
    return repo + uploaded


def read_document_bytes(
    ref: DocumentRef, state: AppState, group: DocumentGroup = USER_STORIES
) -> bytes:
    """Raw content of a selected document (from disk or from the uploaded files)."""
    if ref.path is not None:
        return ref.path.read_bytes()
    return group.uploaded(state)[ref.name]
