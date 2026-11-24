"""Costruzione dei prompt finali (template del prompt + dati da elaborare)."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol


class UiFile(Protocol):
    """Quello che serve del design UI per descriverlo nel prompt (vedi ``services.ui_analysis``)."""

    name: str
    pages: int | None
    pdf_text: str


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROMPT_DIR = PROJECT_ROOT / "parser" / "prompt"
FINAL_PROMPT_DIR = PROJECT_ROOT / "parser" / "finalPrompt"

# Stessi percorsi usati da main.py.
REQUIREMENTS_PROMPT_TEMPLATE = PROMPT_DIR / "parser.md"
REQUIREMENTS_PROMPT_FINAL = FINAL_PROMPT_DIR / "finalParser.md"
UI_PROMPT_TEMPLATE = PROMPT_DIR / "uiParser.md"
UI_PROMPT_FINAL = FINAL_PROMPT_DIR / "finalUi.md"
# Casi di test in due fasi: elenco dei casi per user story, poi step a gruppi di casi.
OUTLINE_PROMPT_TEMPLATE = PROMPT_DIR / "testCaseOutline.md"
TEST_CASES_PROMPT_TEMPLATE = PROMPT_DIR / "testCaseGenerator.md"
TEST_CASES_PROMPT_DIR = FINAL_PROMPT_DIR / "testCases"

_PLACEHOLDER = re.compile(r"\{\{([A-Z_]+)\}\}")
# Alternative blocks of the template: {{#MODALITA nome}} ... {{/MODALITA}} (only one is kept).
_MODE_BLOCK = re.compile(r"\{\{#MODALITA (\w+)\}\}\n(.*?)\{\{/MODALITA\}\}\n?", re.DOTALL)
# Optional blocks, kept only when a UI spec is available.
_UI_BLOCK = re.compile(r"\{\{#SPECIFICA_UI\}\}\n(.*?)\{\{/SPECIFICA_UI\}\}\n?", re.DOTALL)
# Any marker left after the substitutions means a malformed template.
_LEFTOVER = re.compile(r"\{\{[#/]?[A-Z_]+[^}]*\}\}")

_SECTION_RULE = "=" * 50

# How the requested number of test cases must be used.
COUNT_MODE_INDICATIVE = "indicativo"  # impartial analysis, the number is only a reference
COUNT_MODE_PRECISE = "preciso"  # exactly that number, as far as integrity allows
COUNT_MODES = (COUNT_MODE_INDICATIVE, COUNT_MODE_PRECISE)


class PromptBuildError(Exception):
    """Il prompt non può essere costruito o salvato."""


@dataclass(frozen=True)
class InitiativeData:
    """Dati dell'iniziativa inseriti dall'utente (stringa vuota = non fornito)."""

    name: str = ""
    id: str = ""
    epic: str = ""
    requirement_id: str = ""


def _section(title: str, body: str) -> str:
    return f"{_SECTION_RULE}\n{title}\n{_SECTION_RULE}\n\n{body.strip()}\n"


def compact_json(data: Any) -> str:
    """JSON su una riga per elemento, senza indentazione: stesso contenuto, meno token."""
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def _json_literal(value: str | int | None) -> str:
    """Valore come letterale JSON: numero, testo tra doppi apici (escape inclusi) oppure null."""
    if isinstance(value, int):
        return str(value)
    text = (value or "").strip()
    return json.dumps(text, ensure_ascii=False) if text else "null"


def _fill_placeholders(template: str, values: Mapping[str, str | int | None]) -> str:
    """Sostituisce ``{{NOME}}`` con il letterale JSON del valore, in un solo passaggio.

    Un solo passaggio: un valore dell'utente che contiene a sua volta ``{{...}}``
    non viene mai riespanso. I segnaposto non presenti in ``values`` restano invariati.
    """
    return _PLACEHOLDER.sub(
        lambda m: _json_literal(values[m.group(1)]) if m.group(1) in values else m.group(0),
        template,
    )


def _select_mode_blocks(template: str, mode: str) -> str:
    """Keep only the template blocks of ``mode`` (the model never sees the other rules)."""
    return _MODE_BLOCK.sub(lambda m: m.group(2) if m.group(1) == mode else "", template)


def _select_ui_blocks(template: str, with_ui: bool) -> str:
    return _UI_BLOCK.sub(lambda m: m.group(1) if with_ui else "", template)


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


def _render(
    template_file: Path,
    description: str,
    *,
    mode: str = COUNT_MODE_INDICATIVE,
    with_ui: bool = False,
    values: Mapping[str, str | int | None] | None = None,
) -> str:
    """Template con blocchi selezionati e segnaposto sostituiti; errore se resta un marcatore."""
    values = values or {}
    template = _read_text(template_file, description)
    template = _select_mode_blocks(_select_ui_blocks(template, with_ui), mode)
    # Checked before inserting the user's values, which may contain "{{" themselves.
    for marker in _LEFTOVER.finditer(template):
        name = marker.group(0).strip("{}")
        if name not in values:
            raise PromptBuildError(
                f"{description}: marcatore non riconosciuto '{marker.group(0)}' "
                "(i blocchi {{#...}} e {{/...}} devono stare su righe proprie)."
            )
    return _fill_placeholders(template, values)


def _merge_and_save(template: str, data: str, output_file: Path | None) -> str:
    prompt = template + "\n\n" + data
    if output_file is not None:
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
    output_file: Path | None = REQUIREMENTS_PROMPT_FINAL,
) -> str:
    """Prompt 1: template (con i dati utente) + testo dei requisiti raccolti dai documenti.

    ID iniziativa, epica e ID requisito utente vengono inseriti nel template;
    se ``initiative`` manca o un campo è vuoto, il valore è ``null``.
    """
    if not requirements_text.strip():
        raise PromptBuildError("Il testo dei requisiti è vuoto.")
    initiative = initiative or InitiativeData()
    template = _render(
        template_file,
        "Template del prompt 1",
        values={
            "INIZIATIVA_ID": initiative.id,
            "EPIC_ID": initiative.epic,
            "USER_REQUIREMENT_ID": initiative.requirement_id,
        },
    )
    return _merge_and_save(template, requirements_text, output_file)


def build_ui_prompt(
    files: Sequence[UiFile],
    requirements_json: str,
    template_file: Path = UI_PROMPT_TEMPLATE,
    output_file: Path | None = UI_PROMPT_FINAL,
) -> str:
    """Prompt UI: template + elenco dei design, testo dei PDF e JSON dei requisiti.

    I file veri e propri (immagini e PDF) non sono nel testo: vengono allegati alla
    richiesta da ``services.ui_analysis``.
    """
    if not files:
        raise PromptBuildError("Nessun design UI da analizzare.")
    if not requirements_json.strip():
        raise PromptBuildError("Il JSON dei requisiti è vuoto.")

    listing = "\n".join(
        f"- {f.name} (PDF, {f.pages} pagine)" if f.pages else f"- {f.name} (immagine PNG)"
        for f in files
    )
    pdf_texts = [
        f"# FILE: {f.name}\n\n{f.pdf_text}\n\n# FINE FILE: {f.name}" for f in files if f.pdf_text
    ]
    data = "\n".join(
        [
            _section("FILE UI RICEVUTI", listing),
            _section(
                "TESTO ESTRATTO DAI PDF",
                "\n\n".join(pdf_texts) or "Nessun testo selezionabile nei PDF ricevuti.",
            ),
            _section("REQUISITI (solo per collegare le schermate)", requirements_json),
        ]
    )
    return _merge_and_save(_render(template_file, "Template del prompt UI"), data, output_file)


def build_outline_prompt(
    requirements: Sequence[Mapping[str, Any]],
    ui_spec: Mapping[str, Any] | None,
    known_titles: Sequence[str],
    target_count: int | None,
    template_file: Path = OUTLINE_PROMPT_TEMPLATE,
    output_file: Path | None = None,
) -> str:
    """Fase A: elenco dei casi di test di una user story (``requirements`` con il campo ``ref``).

    ``target_count`` è il numero di casi richiesto per questa user story (modalità
    preciso) oppure ``None`` (modalità indicativa: decide il modello).
    """
    if not requirements:
        raise PromptBuildError("Nessun requisito per la user story.")
    precise = target_count is not None and target_count > 0
    mode = COUNT_MODE_PRECISE if precise else COUNT_MODE_INDICATIVE
    template = _render(
        template_file,
        "Template del prompt elenco casi",
        mode=mode,
        with_ui=bool(ui_spec),
        values={
            "NUMERO_CASI_TEST": target_count if precise else None,
            "MODALITA_NUMERO_CASI_TEST": mode,
        },
    )
    sections = [_section("REQUISITI DELLA USER STORY", compact_json(list(requirements)))]
    if ui_spec:
        sections.append(_section("SPECIFICA UI", compact_json(ui_spec)))
    sections.append(
        _section(
            "CASI GIÀ INDIVIDUATI (altre user story)",
            "\n".join(f"- {title}" for title in known_titles) or "Nessuno.",
        )
    )
    return _merge_and_save(template, "\n".join(sections), output_file)


def build_detail_prompt(
    cases: Sequence[Mapping[str, Any]],
    requirements: Sequence[Mapping[str, Any]],
    ui_spec: Mapping[str, Any] | None,
    corrections: Sequence[str] = (),
    template_file: Path = TEST_CASES_PROMPT_TEMPLATE,
    output_file: Path | None = None,
) -> str:
    """Fase B: step dei ``cases`` (con ``case_ref``) di una user story.

    ``corrections`` elenca gli errori di un tentativo precedente da correggere.
    """
    if not cases:
        raise PromptBuildError("Nessun caso di test da dettagliare.")
    template = _render(template_file, "Template del prompt step", with_ui=bool(ui_spec))
    sections = [
        _section("CASI DA DETTAGLIARE", compact_json(list(cases))),
        _section("REQUISITI DELLA USER STORY", compact_json(list(requirements))),
    ]
    if ui_spec:
        sections.append(_section("SPECIFICA UI", compact_json(ui_spec)))
    if corrections:
        sections.append(
            _section(
                "CORREZIONI RICHIESTE",
                "Un tentativo precedente non rispettava queste regole. Correggile:\n"
                + "\n".join(f"- {c}" for c in corrections),
            )
        )
    return _merge_and_save(template, "\n".join(sections), output_file)
