"""Costruzione dei prompt finali (template del prompt + dati da elaborare)."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Stessi percorsi usati da main.py per il Prompt 1.
REQUIREMENTS_PROMPT_TEMPLATE = PROJECT_ROOT / "parser" / "prompt" / "parser.md"
REQUIREMENTS_PROMPT_FINAL = PROJECT_ROOT / "parser" / "finalPrompt" / "finalParser.md"


class PromptBuildError(Exception):
    """Il prompt non può essere costruito o salvato."""


def build_requirements_prompt(
    requirements_text: str,
    template_file: Path = REQUIREMENTS_PROMPT_TEMPLATE,
    output_file: Path = REQUIREMENTS_PROMPT_FINAL,
) -> str:
    """Unisce il template del Prompt 1 al testo dei requisiti e salva il risultato."""
    if not requirements_text.strip():
        raise PromptBuildError("Il testo dei requisiti è vuoto.")
    if not template_file.is_file():
        raise PromptBuildError(f"Template del prompt non trovato: {template_file}")

    try:
        template = template_file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise PromptBuildError(f"Template del prompt non leggibile: {exc}") from exc
    if not template.strip():
        raise PromptBuildError(f"Il template del prompt è vuoto: {template_file}")

    prompt = template + "\n\n" + requirements_text

    try:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(prompt, encoding="utf-8")
    except OSError as exc:
        raise PromptBuildError(f"Impossibile salvare il prompt finale: {exc}") from exc
    return prompt
