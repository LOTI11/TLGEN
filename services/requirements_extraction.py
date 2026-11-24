"""Estrazione dei requisiti dalle user story (prompt 1), con risposta sempre completa.

Di norma tutti i documenti vanno in una sola richiesta. Se la risposta supera il
massimo di token in uscita, i documenti vengono divisi in due gruppi (e così
via) e i requisiti uniti: nessun requisito viene perso per un troncamento.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from services.json_generation import (
    REQUIREMENTS_JSON_FILE,
    REQUIREMENTS_RAW_FILE,
    JsonGenerationError,
    request_json,
    require_list,
    save_json,
    split_on_truncation,
)
from services.llm_types import JsonLlmClient, StatusCallback
from services.prompt_builder import (
    REQUIREMENTS_PROMPT_FINAL,
    InitiativeData,
    build_requirements_prompt,
)

REQUIREMENTS_THINKING_BUDGET = 8192


@dataclass(frozen=True)
class RequirementsExtraction:
    data: dict[str, Any]
    text: str  # JSON formattato, come salvato su file
    parts: int
    usage: list[str]


def merge_requirement_parts(parts: Sequence[dict[str, Any]]) -> dict[str, Any]:
    if len(parts) == 1:
        return parts[0]
    return {
        "source_files": [f for part in parts for f in part.get("source_files") or []],
        "requirements": [r for part in parts for r in part.get("requirements") or []],
    }


def extract_requirements(
    document_texts: Sequence[str],
    initiative: InitiativeData,
    llm: JsonLlmClient,
    on_status: StatusCallback | None = None,
    raw_file: Path = REQUIREMENTS_RAW_FILE,
    json_file: Path = REQUIREMENTS_JSON_FILE,
    prompt_file: Path | None = REQUIREMENTS_PROMPT_FINAL,
) -> RequirementsExtraction:
    """Estrae i requisiti dai documenti (testo già racchiuso tra FILE / FINE FILE)."""
    usage: list[str] = []

    def run(subset: Sequence[str]) -> dict[str, Any]:
        prompt = build_requirements_prompt("\n".join(subset), initiative, output_file=prompt_file)
        if on_status:
            on_status(f"Extracting requirements from {len(subset)} documents…")
        data, result = request_json(
            llm,
            prompt,
            thinking_budget=REQUIREMENTS_THINKING_BUDGET,
            raw_file=raw_file,
            check=lambda d: require_list(d, "requirements"),
            on_status=on_status,
        )
        usage.append(result.usage())
        return data

    def split(first: int, second: int) -> None:
        if on_status:
            on_status(f"Response too long: splitting the documents into {first} + {second}…")

    parts = split_on_truncation(list(document_texts), run, on_split=split)
    data = merge_requirement_parts(parts)
    if not data.get("requirements"):
        raise JsonGenerationError("Il modello non ha estratto alcun requisito dai documenti.")
    return RequirementsExtraction(data, save_json(data, json_file), len(parts), usage)
