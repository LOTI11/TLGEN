"""Richieste JSON al modello, con controllo di completezza e divisione del lavoro.

Ogni risposta deve essere completa e valida: se il modello la tronca (massimo di
token in uscita) il chiamante divide il lavoro in due metà con
``split_on_truncation`` invece di ripetere la stessa richiesta. Se il JSON non è
valido la richiesta viene ripetuta una volta; non c'è riparazione automatica,
che nasconderebbe dati mancanti.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any, TypeVar

from services.llm_types import (
    Attachment,
    JsonLlmClient,
    LlmResult,
    StatusCallback,
    TruncatedResponseError,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_INPUT = PROJECT_ROOT / "data" / "input"

# Stessi file usati da main.py per i requisiti.
REQUIREMENTS_RAW_FILE = DATA_INPUT / "prova.txt"
REQUIREMENTS_JSON_FILE = DATA_INPUT / "jsonAI" / "requirements.json"
TEST_CASES_JSON_FILE = DATA_INPUT / "jsonAI" / "test_cases.json"

MAX_ATTEMPTS = 2

T = TypeVar("T")
R = TypeVar("R")


class JsonGenerationError(Exception):
    """La generazione, la validazione o il salvataggio del JSON non sono riusciti."""


def strip_json_fence(response: str) -> str:
    """Rimuove il recinto ```json ... ``` se presente; altrimenti restituisce il testo."""
    lines = response.strip().splitlines()
    if lines and lines[0].strip().lower() == "```json":
        if lines[-1].strip() != "```":
            raise JsonGenerationError(
                "La risposta JSON inizia con ```json ma non termina con ```"
            )
        return chr(10).join(lines[1:-1]).strip()
    return response.strip()


def write_text(path: Path, text: str) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    except OSError as exc:
        raise JsonGenerationError(f"Impossibile salvare {path.name}: {exc}") from exc


def save_json(data: Any, json_file: Path) -> str:
    """Salva ``data`` formattato e restituisce il testo salvato."""
    text = json.dumps(data, indent=4, ensure_ascii=False)
    write_text(json_file, text)
    return text


def require_list(data: Any, key: str) -> list[Any]:
    """La lista ``key`` del JSON (anche vuota); errore se manca o non è una lista."""
    items = data.get(key) if isinstance(data, dict) else None
    if not isinstance(items, list):
        raise JsonGenerationError(f"Il JSON non contiene la lista '{key}'.")
    return items


def request_json(
    llm: JsonLlmClient,
    prompt: str,
    *,
    files: Sequence[Attachment] = (),
    schema: Any = None,
    thinking_budget: int | None = None,
    raw_file: Path | None = None,
    check: Callable[[Any], None] | None = None,
    on_status: StatusCallback | None = None,
    max_attempts: int = MAX_ATTEMPTS,
) -> tuple[Any, LlmResult]:
    """Invia ``prompt`` e restituisce il JSON della risposta con il risultato della chiamata.

    ``check`` valida il contenuto (solleva ``JsonGenerationError`` se non va bene).
    ``TruncatedResponseError`` non viene gestito qui: è il segnale per dividere il lavoro.
    """
    last_error = ""
    for attempt in range(1, max_attempts + 1):
        if attempt > 1 and on_status:
            on_status(f"Invalid JSON, asking the model again (attempt {attempt}/{max_attempts})…")
        result = llm.generate_json(
            prompt,
            files=files,
            schema=schema,
            thinking_budget=thinking_budget,
            on_status=on_status,
        )
        if raw_file is not None:
            write_text(raw_file, result.text)
        try:
            data = json.loads(strip_json_fence(result.text))
            if check is not None:
                check(data)
        except (json.JSONDecodeError, JsonGenerationError) as exc:
            last_error = str(exc)
            continue
        return data, result
    raise JsonGenerationError(
        f"La risposta del modello non è un JSON valido dopo {max_attempts} tentativi ({last_error})."
    )


def split_on_truncation(
    items: Sequence[T],
    run: Callable[[Sequence[T]], R],
    on_split: Callable[[int, int], None] | None = None,
) -> list[R]:
    """Esegue ``run(items)``; se la risposta è troncata divide ``items`` a metà e ripete.

    Restituisce un risultato per ogni parte, nell'ordine degli elementi. ``on_split``
    riceve le dimensioni delle due metà. Se anche un solo elemento è troppo grande
    solleva ``JsonGenerationError``.
    """
    try:
        return [run(items)]
    except TruncatedResponseError as exc:
        if len(items) <= 1:
            raise JsonGenerationError(
                "La risposta del modello è troncata anche per un singolo elemento: "
                f"{exc}"
            ) from exc
        middle = len(items) // 2
        if on_split:
            on_split(middle, len(items) - middle)
        return split_on_truncation(items[:middle], run, on_split) + split_on_truncation(
            items[middle:], run, on_split
        )
