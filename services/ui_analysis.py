"""Analisi dei design UI esportati da Figma (PNG e PDF).

Tutti i file selezionati vengono inviati a Gemini in un'unica richiesta, così il
modello vede insieme schermate, stati e passaggi dello stesso flusso; solo se la
risposta supera il massimo di token i design vengono divisi in più richieste. Per i PDF
viene inviato anche il testo estratto (più affidabile della lettura
dell'immagine per le etichette). Il risultato è la SPECIFICA UI in JSON, usata
poi dal prompt dei casi di test come fonte integrativa.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Any

from pypdf import PdfReader

from services.input_preparation import SourceDocument
from services.json_generation import (
    DATA_INPUT,
    request_json,
    require_list,
    save_json,
    split_on_truncation,
)
from services.llm_types import JsonLlmClient, StatusCallback

# Token di ragionamento per l'analisi dei design: il resto del massimo in uscita
# resta alla risposta.
UI_THINKING_BUDGET = 8192

UI_SPEC_RAW_FILE = DATA_INPUT / "provaUi.txt"
UI_SPEC_JSON_FILE = DATA_INPUT / "jsonAI" / "ui_spec.json"

UI_MIME_TYPES: dict[str, str] = {".png": "image/png", ".pdf": "application/pdf"}

_MIB = 1024 * 1024

# Limiti Vertex AI per Gemini 2.5 con dati inline. Si usano i valori validi sia
# per gli endpoint standard (256 MB per file, 500 MiB per richiesta) sia per
# quelli non migrati (30 MiB per immagine, 50 MiB per PDF, 1.000 pagine PDF).
MAX_FILE_BYTES: dict[str, int] = {".png": 30 * _MIB, ".pdf": 50 * _MIB}
# Totale dei file: la codifica base64 aggiunge circa il 33%, quindi
# 300 MiB diventano circa 400 MiB, sotto i 500 MiB della richiesta.
MAX_TOTAL_BYTES = 300 * _MIB
MAX_PDF_PAGES = 1000
MAX_FILES = 3000

_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


class UiAnalysisError(Exception):
    """I design UI non sono utilizzabili o l'analisi non è riuscita."""


@dataclass(frozen=True)
class UiFile:
    """Un design pronto per l'invio: contenuto, mime type e (per i PDF) testo estratto."""

    name: str
    content: bytes
    mime_type: str
    pages: int | None = None  # solo PDF
    pdf_text: str = ""  # solo PDF; vuoto se il PDF non contiene testo selezionabile

    @property
    def file_type(self) -> str:
        return Path(self.name).suffix.lstrip(".").lower()


def _read_pdf(document: SourceDocument) -> tuple[int, str]:
    try:
        reader = PdfReader(BytesIO(document.content))
        pages = [(page.extract_text() or "").strip() for page in reader.pages]
    except Exception as exc:  # file corrotto o cifrato
        raise UiAnalysisError(f"{document.name}: PDF non leggibile ({exc}).") from exc
    if not pages:
        raise UiAnalysisError(f"{document.name}: il PDF non contiene pagine.")
    text = "\n\n".join(
        f"[Pagina {number}]\n{content}" for number, content in enumerate(pages, start=1) if content
    )
    return len(pages), text


def prepare_ui_files(documents: Sequence[SourceDocument]) -> list[UiFile]:
    """Controlla i design e li prepara per l'invio; segnala insieme tutti i problemi."""
    files: list[UiFile] = []
    errors: list[str] = []
    for document in documents:
        suffix = Path(document.name).suffix.lower()
        mime_type = UI_MIME_TYPES.get(suffix)
        if mime_type is None:
            errors.append(f"{document.name}: formato '{suffix}' non supportato (solo PNG o PDF).")
            continue
        if not document.content:
            errors.append(f"{document.name}: file vuoto.")
            continue
        if len(document.content) > MAX_FILE_BYTES[suffix]:
            errors.append(
                f"{document.name}: pesa {len(document.content) / _MIB:.1f} MB, il massimo per "
                f"un file {suffix.lstrip('.').upper()} è {MAX_FILE_BYTES[suffix] // _MIB} MB."
            )
            continue
        if suffix == ".png":
            if not document.content.startswith(_PNG_SIGNATURE):
                errors.append(f"{document.name}: non è un'immagine PNG valida.")
                continue
            files.append(UiFile(document.name, document.content, mime_type))
            continue
        try:
            pages, text = _read_pdf(document)
        except UiAnalysisError as exc:
            errors.append(str(exc))
            continue
        files.append(UiFile(document.name, document.content, mime_type, pages, text))

    if len(files) > MAX_FILES:
        errors.append(f"Troppi design selezionati ({len(files)}): il massimo è {MAX_FILES}.")
    total = sum(len(f.content) for f in files)
    if total > MAX_TOTAL_BYTES:
        errors.append(
            f"I design selezionati pesano {total / _MIB:.1f} MB: il massimo per "
            f"un'analisi è {MAX_TOTAL_BYTES // _MIB} MB. Riduci il numero di file "
            "o esporta i PNG a una risoluzione minore."
        )
    pages = sum(f.pages or 0 for f in files)
    if pages > MAX_PDF_PAGES:
        errors.append(
            f"I PDF selezionati hanno {pages} pagine in totale: il massimo è {MAX_PDF_PAGES}."
        )
    if errors:
        raise UiAnalysisError("\n".join(errors))
    if not files:
        raise UiAnalysisError("Nessun design UI selezionato.")
    return files


@dataclass(frozen=True)
class UiAnalysis:
    data: dict[str, Any]
    text: str  # JSON formattato, come salvato su file
    parts: int  # richieste necessarie (più di una se la risposta era troppo lunga)
    usage: list[str]


def _prefix_ids(part: dict[str, Any], prefix: str) -> dict[str, Any]:
    """Rende univoci gli screen_id di una parte quando i design sono stati divisi."""
    def rename(value: Any) -> Any:
        return f"{prefix}{value}" if isinstance(value, str) and value else value

    screens = []
    for screen in part.get("screens", []):
        screen = dict(screen, screen_id=rename(screen.get("screen_id")))
        screen["navigation"] = [
            dict(nav, target_screen_id=rename(nav.get("target_screen_id")))
            for nav in screen.get("navigation") or []
        ]
        screens.append(screen)
    flows = [
        dict(flow, screen_ids=[rename(s) for s in flow.get("screen_ids") or []])
        for flow in part.get("flows") or []
    ]
    return dict(part, screens=screens, flows=flows)


def merge_ui_parts(parts: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """Unisce le SPECIFICHE UI di più richieste in una sola."""
    if len(parts) == 1:
        return parts[0]
    merged: dict[str, Any] = {"ui_sources": [], "screens": [], "flows": [], "open_points": []}
    for number, part in enumerate(parts, start=1):
        part = _prefix_ids(part, f"P{number}-")
        for key in merged:
            merged[key].extend(part.get(key) or [])
    return merged


def analyze_ui(
    files: Sequence[UiFile],
    requirements_json: str,
    llm: JsonLlmClient,
    on_status: StatusCallback | None = None,
    raw_file: Path = UI_SPEC_RAW_FILE,
    json_file: Path = UI_SPEC_JSON_FILE,
    prompt_file: Path | None = None,
) -> UiAnalysis:
    """Invia i design a Gemini e salva la SPECIFICA UI (lista ``screens``).

    Se la risposta è troncata i design vengono divisi in due gruppi (e così via)
    e i risultati uniti: nessuna schermata viene persa.
    """
    from services.prompt_builder import UI_PROMPT_FINAL, build_ui_prompt  # evita import circolare

    usage: list[str] = []

    def run(subset: Sequence[UiFile]) -> dict[str, Any]:
        prompt = build_ui_prompt(subset, requirements_json, output_file=prompt_file or UI_PROMPT_FINAL)
        if on_status:
            on_status(f"Analyzing {len(subset)} designs…")
        data, result = request_json(
            llm,
            prompt,
            files=[(f.name, f.content, f.mime_type) for f in subset],
            thinking_budget=UI_THINKING_BUDGET,
            raw_file=raw_file,
            check=lambda d: require_list(d, "screens"),
            on_status=on_status,
        )
        usage.append(result.usage())
        return data

    def split(first: int, second: int) -> None:
        if on_status:
            on_status(f"Response too long: splitting the designs into {first} + {second} files…")

    parts = split_on_truncation(list(files), run, on_split=split)
    data = merge_ui_parts(parts)
    return UiAnalysis(data, save_json(data, json_file), len(parts), usage)
