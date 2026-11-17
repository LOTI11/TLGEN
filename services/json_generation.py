"""Generazione di un file JSON a partire da un prompt inviato a Gemini.

Logica condivisa dalle fasi "requisiti" e "test case" (stessi file di main.py): invia il prompt, toglie
l'eventuale recinto ```json, salva il testo grezzo in un file di appoggio e
salva il JSON formattato.

Se la risposta non è un JSON valido il modello viene richiamato (fino a
``MAX_ATTEMPTS`` tentativi in totale); come ultima risorsa il JSON viene
riparato automaticamente e il risultato è marcato come ``repaired``.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

import json_repair

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_INPUT = PROJECT_ROOT / "data" / "input"

# Stessi file usati da main.py per i requisiti.
REQUIREMENTS_RAW_FILE = DATA_INPUT / "prova.txt"
REQUIREMENTS_JSON_FILE = DATA_INPUT / "jsonAI" / "requirements.json"
TEST_CASES_RAW_FILE = DATA_INPUT / "provaTest.txt"
TEST_CASES_JSON_FILE = DATA_INPUT / "jsonAI" / "test_cases.json"


MAX_ATTEMPTS = 3


class JsonGenerationError(Exception):
    """La generazione, il parsing o il salvataggio del JSON non sono riusciti."""


class LlmClient(Protocol):
    def generate_response(self, prompt: str) -> str: ...


@dataclass(frozen=True)
class GeneratedJson:
    data: Any
    text: str  # JSON formattato, come salvato su file
    attempts: int = 1
    repaired: bool = False


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


def _write(path: Path, text: str) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    except OSError as exc:
        raise JsonGenerationError(f"Impossibile salvare {path.name}: {exc}") from exc


def _repair(text: str, items_key: str | None) -> Any:
    """Ripara un JSON malformato; rifiuta risultati vuoti o privi della lista attesa."""
    try:
        data = json_repair.loads(text)
    except Exception as exc:  # il testo non è recuperabile
        raise JsonGenerationError(f"Riparazione del JSON non riuscita: {exc}") from exc
    if not isinstance(data, (dict, list)) or not data:
        raise JsonGenerationError("Riparazione del JSON non riuscita: nessun dato recuperato.")
    if items_key is not None:
        items = data.get(items_key) if isinstance(data, dict) else None
        if not isinstance(items, list) or not items:
            raise JsonGenerationError(
                f"JSON riparato ma privo della lista '{items_key}': risposta non affidabile."
            )
    return data


def generate_json_file(
    prompt: str,
    raw_file: Path,
    json_file: Path,
    llm: LlmClient,
    items_key: str | None = None,
    on_status: Callable[[str], None] | None = None,
    max_attempts: int = MAX_ATTEMPTS,
) -> GeneratedJson:
    """Invia ``prompt`` al modello e salva risposta grezza (``raw_file``) e JSON (``json_file``).

    ``items_key`` è la lista che il JSON deve contenere (usata per validare
    un eventuale JSON riparato). ``on_status`` riceve messaggi di avanzamento.
    """

    def status(message: str) -> None:
        if on_status:
            on_status(message)

    last_text = ""
    last_error = ""
    for attempt in range(1, max_attempts + 1):
        status(
            "Waiting for the model response…"
            if attempt == 1
            else f"Invalid JSON, asking the model again (attempt {attempt}/{max_attempts})…"
        )
        try:
            response = llm.generate_response(prompt)
        except Exception as exc:  # rete/credenziali/quota: non ha senso riprovare
            raise JsonGenerationError(f"Chiamata al modello non riuscita: {exc}") from exc

        try:
            last_text = strip_json_fence(response)
        except JsonGenerationError as exc:  # recinto non chiuso: risposta da rifare
            last_text, last_error = response.strip(), str(exc)
            _write(raw_file, last_text)
            continue

        _write(raw_file, last_text)
        try:
            data = json.loads(last_text)
        except json.JSONDecodeError as exc:
            last_error = str(exc)
            continue
        return _save(data, json_file, attempt, repaired=False)

    status("Repairing the JSON automatically…")
    try:
        data = _repair(last_text, items_key)
    except JsonGenerationError as exc:
        raise JsonGenerationError(
            f"La risposta del modello non è un JSON valido dopo {max_attempts} tentativi "
            f"({last_error}). {exc} Testo grezzo salvato in {raw_file}."
        ) from exc
    return _save(data, json_file, max_attempts, repaired=True)


def _save(data: Any, json_file: Path, attempts: int, repaired: bool) -> GeneratedJson:
    text = json.dumps(data, indent=4, ensure_ascii=False)
    _write(json_file, text)
    return GeneratedJson(data, text, attempts, repaired)
