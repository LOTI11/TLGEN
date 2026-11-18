"""Costruzione dei prompt finali (template del prompt + dati da elaborare)."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from services.json_generation import REQUIREMENTS_JSON_FILE

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROMPT_DIR = PROJECT_ROOT / "parser" / "prompt"
FINAL_PROMPT_DIR = PROJECT_ROOT / "parser" / "finalPrompt"

# Stessi percorsi usati da main.py.
REQUIREMENTS_PROMPT_TEMPLATE = PROMPT_DIR / "parser.md"
REQUIREMENTS_PROMPT_FINAL = FINAL_PROMPT_DIR / "finalParser.md"
TEST_CASES_PROMPT_TEMPLATE = PROMPT_DIR / "testCaseGenerator.md"
TEST_CASES_PROMPT_FINAL = FINAL_PROMPT_DIR / "finalTestCases.md"

_PLACEHOLDER = re.compile(r"\{\{([A-Z_]+)\}\}")


class PromptBuildError(Exception):
    """Il prompt non può essere costruito o salvato."""


@dataclass(frozen=True)
class InitiativeData:
    """Dati dell'iniziativa inseriti dall'utente (stringa vuota = non fornito)."""

    name: str = ""
    id: str = ""
    epic: str = ""
    requirement_id: str = ""


def _json_literal(value: str | None) -> str:
    """Valore come letterale JSON: testo tra doppi apici (escape inclusi) oppure null."""
    text = (value or "").strip()
    return json.dumps(text, ensure_ascii=False) if text else "null"


def _fill_placeholders(template: str, values: Mapping[str, str | None]) -> str:
    """Sostituisce ``{{NOME}}`` con il letterale JSON del valore, in un solo passaggio.

    Un solo passaggio: un valore dell'utente che contiene a sua volta ``{{...}}``
    non viene mai riespanso. I segnaposto non presenti in ``values`` restano invariati.
    """
    return _PLACEHOLDER.sub(
        lambda m: _json_literal(values[m.group(1)]) if m.group(1) in values else m.group(0),
        template,
    )


def _read_text(path: Path, description: str) -> str:
    if not path.is_file():
        raise PromptBuildError(f"{description} non trovato: {path}")
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise PromptBuildError(f"{description} non leggibile: {exc}") from exc
    if not text.strip():
        raise PromptBuildError(f"{description} è vuoto: {path}")
    return text


def _merge_and_save(template: str, data: str, output_file: Path) -> str:
    prompt = template + "\n\n" + data
    try:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(prompt, encoding="utf-8")
    except OSError as exc:
        raise PromptBuildError(f"Impossibile salvare il prompt finale: {exc}") from exc
    return prompt


def build_requirements_prompt(
    requirements_text: str,
    initiative: InitiativeData | None = None,
    template_file: Path = REQUIREMENTS_PROMPT_TEMPLATE,
    output_file: Path = REQUIREMENTS_PROMPT_FINAL,
) -> str:
    """Prompt 1: template (con i dati utente) + testo dei requisiti raccolti dai documenti.

    ID iniziativa, epica e ID requisito utente vengono inseriti nel template;
    se ``initiative`` manca o un campo è vuoto, il valore è ``null``.
    """
    if not requirements_text.strip():
        raise PromptBuildError("Il testo dei requisiti è vuoto.")
    initiative = initiative or InitiativeData()
    template = _fill_placeholders(
        _read_text(template_file, "Template del prompt 1"),
        {
            "INIZIATIVA_ID": initiative.id,
            "EPIC_ID": initiative.epic,
            "USER_REQUIREMENT_ID": initiative.requirement_id,
        },
    )
    return _merge_and_save(template, requirements_text, output_file)


def build_test_cases_prompt(
    initiative: InitiativeData | None = None,
    requirements_json_file: Path = REQUIREMENTS_JSON_FILE,
    template_file: Path = TEST_CASES_PROMPT_TEMPLATE,
    output_file: Path = TEST_CASES_PROMPT_FINAL,
) -> str:
    """Prompt 2: template (con il nome iniziativa) + JSON dei requisiti generato dal Prompt 1.

    ID iniziativa, epica e ID requisito utente non passano da qui: il modello li
    copia dal file dei requisiti. Il nome iniziativa (macro area) viene inserito
    nel template; se manca vale ``null``.
    """
    initiative = initiative or InitiativeData()
    template = _fill_placeholders(
        _read_text(template_file, "Template del prompt 2"),
        {"NOME_INIZIATIVA": initiative.name},
    )
    requirements_json = _read_text(requirements_json_file, "File JSON dei requisiti")
    return _merge_and_save(template, requirements_json, output_file)
