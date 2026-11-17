"""Costruzione dei prompt finali (template del prompt + dati da elaborare)."""

from __future__ import annotations

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


class PromptBuildError(Exception):
    """Il prompt non può essere costruito o salvato."""


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
    template_file: Path = REQUIREMENTS_PROMPT_TEMPLATE,
    output_file: Path = REQUIREMENTS_PROMPT_FINAL,
) -> str:
    """Prompt 1: template + testo dei requisiti raccolti dai documenti."""
    if not requirements_text.strip():
        raise PromptBuildError("Il testo dei requisiti è vuoto.")
    template = _read_text(template_file, "Template del prompt 1")
    return _merge_and_save(template, requirements_text, output_file)


def build_test_cases_prompt(
    requirements_json_file: Path = REQUIREMENTS_JSON_FILE,
    template_file: Path = TEST_CASES_PROMPT_TEMPLATE,
    output_file: Path = TEST_CASES_PROMPT_FINAL,
) -> str:
    """Prompt 2: template + JSON dei requisiti generato dal Prompt 1."""
    template = _read_text(template_file, "Template del prompt 2")
    requirements_json = _read_text(requirements_json_file, "File JSON dei requisiti")
    return _merge_and_save(template, requirements_json, output_file)
