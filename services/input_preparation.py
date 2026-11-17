"""Preparazione degli input: legge i documenti scelti dall'utente e costruisce
il testo dei requisiti (equivalente di ``MarkdownReader().read_all()``, ma
sui documenti selezionati invece che su una cartella fissa).
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from docx import Document
from pypdf import PdfReader

from dev.ReqCollector import MarkdownReader

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# File di appoggio con il testo dei requisiti, usato dallo step successivo (Prompt 1).
REQUIREMENTS_TEXT_FILE = PROJECT_ROOT / "data" / "input" / "requirements_text.md"

# Callback (indice 1-based, totale, nome documento) chiamata prima di leggere ogni documento.
ProgressCallback = Callable[[int, int, str], None]


class DocumentReadError(Exception):
    """Uno o più documenti non sono leggibili."""


@dataclass(frozen=True)
class SourceDocument:
    name: str
    content: bytes


def _decode_text(content: bytes) -> str:
    return content.decode("utf-8-sig")


def _read_docx(content: bytes) -> str:
    document = Document(BytesIO(content))
    parts = [p.text for p in document.paragraphs if p.text.strip()]
    for table in document.tables:
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells]
            if any(cells):
                parts.append(" | ".join(cells))
    return "\n".join(parts)


def _read_pdf(content: bytes) -> str:
    reader = PdfReader(BytesIO(content))
    return "\n".join((page.extract_text() or "") for page in reader.pages)


_READERS: dict[str, Callable[[bytes], str]] = {
    ".md": _decode_text,
    ".json": _decode_text,
    ".docx": _read_docx,
    ".pdf": _read_pdf,
}


def extract_text(document: SourceDocument) -> str:
    """Estrae il testo di un documento; solleva DocumentReadError se non possibile."""
    suffix = Path(document.name).suffix.lower()
    reader = _READERS.get(suffix)
    if reader is None:
        raise DocumentReadError(
            f"{document.name}: formato '{suffix}' non convertibile in testo."
        )
    try:
        text = reader(document.content).strip()
    except Exception as exc:  # file corrotto, cifrato, encoding errato, ...
        raise DocumentReadError(f"{document.name}: lettura non riuscita ({exc}).") from exc
    if not text:
        raise DocumentReadError(f"{document.name}: nessun testo estratto.")
    return text


def build_requirements_text(
    documents: Sequence[SourceDocument],
    on_progress: ProgressCallback | None = None,
) -> str:
    """Legge tutti i documenti e li unisce nel formato di ``MarkdownReader.read_all()``.

    Se uno o più documenti non sono leggibili solleva un unico DocumentReadError
    che li elenca tutti.
    """
    if not documents:
        raise DocumentReadError("Nessun documento selezionato.")

    contents: list[str] = []
    errors: list[str] = []
    for index, document in enumerate(documents, start=1):
        if on_progress:
            on_progress(index, len(documents), document.name)
        try:
            text = extract_text(document)
        except DocumentReadError as exc:
            errors.append(str(exc))
        else:
            contents.append(MarkdownReader.format_document(document.name, text))

    if errors:
        raise DocumentReadError("\n".join(errors))
    return "\n".join(contents)


def save_requirements_text(text: str, path: Path = REQUIREMENTS_TEXT_FILE) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path
