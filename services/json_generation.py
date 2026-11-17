"""Generazione di un file JSON a partire da un prompt inviato a Gemini.

Logica condivisa dalle fasi "requisiti" e "test case": invia il prompt, toglie
l'eventuale recinto ```json, salva il testo grezzo in un file di appoggio e
salva il JSON formattato.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_INPUT = PROJECT_ROOT / "data" / "input"

# Stessi file usati da main.py per i requisiti.
REQUIREMENTS_RAW_FILE = DATA_INPUT / "prova.txt"
REQUIREMENTS_JSON_FILE = DATA_INPUT / "jsonAI" / "requirements.json"


class JsonGenerationError(Exception):
    """La generazione, il parsing o il salvataggio del JSON non sono riusciti."""


class LlmClient(Protocol):
    def generate_response(self, prompt: str) -> str: ...


@dataclass(frozen=True)
class GeneratedJson:
    data: Any
    text: str  # JSON formattato, come salvato su file


def strip_json_fence(response: str) -> str:
    """Rimuove il recinto ```json ... ``` se presente; altrimenti restituisce il testo."""
    lines = response.strip().splitlines()
    if lines and lines[0].strip().lower() == "```json":
        if lines[-1].strip() != "```":
            raise JsonGenerationError(
                "La risposta JSON inizia con ```json ma non termina con ```"
            )
        return "\n".join(lines[1:-1]).strip()
    return response.strip()


def generate_json_file(
    prompt: str,
    raw_file: Path,
    json_file: Path,
    llm: LlmClient,
) -> GeneratedJson:
    """Invia ``prompt`` al modello e salva risposta grezza (``raw_file``) e JSON (``json_file``)."""
    try:
        response = llm.generate_response(prompt)
    except Exception as exc:  # errori di rete/credenziali/API dell'SDK Google
        raise JsonGenerationError(f"Chiamata al modello non riuscita: {exc}") from exc

    cleaned = strip_json_fence(response)
    try:
        raw_file.parent.mkdir(parents=True, exist_ok=True)
        raw_file.write_text(cleaned, encoding="utf-8")
    except OSError as exc:
        raise JsonGenerationError(f"Impossibile salvare {raw_file.name}: {exc}") from exc

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise JsonGenerationError(
            f"La risposta del modello non è un JSON valido ({exc}). "
            f"Testo grezzo salvato in {raw_file}."
        ) from exc

    text = json.dumps(data, indent=4, ensure_ascii=False)
    try:
        json_file.parent.mkdir(parents=True, exist_ok=True)
        json_file.write_text(text, encoding="utf-8")
    except OSError as exc:
        raise JsonGenerationError(f"Impossibile salvare {json_file.name}: {exc}") from exc
    return GeneratedJson(data, text)
