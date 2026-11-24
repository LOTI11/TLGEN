"""Prompt construction with the user's initiative data (no LLM calls)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from models.TestCase import TestCase  # noqa: E402
from services.prompt_builder import (  # noqa: E402
    OUTLINE_PROMPT_TEMPLATE,
    REQUIREMENTS_PROMPT_TEMPLATE,
    TEST_CASES_PROMPT_TEMPLATE,
    InitiativeData,
    PromptBuildError,
    _render,
    build_detail_prompt,
    build_outline_prompt,
    build_requirements_prompt,
)

INITIATIVE = InitiativeData(
    name="Gestione abbonamento", id="1234567", epic="EP-100", requirement_id="XX12345"
)
REQUIREMENTS = [{"ref": "R1", "title": "Cambio piano", "acceptance_criteria": ["A"]}]
UI = {"screens": [{"screen_id": "S1", "name": "Home", "elements": [{"label": "Conferma"}]}]}
CASES = [{"case_ref": "C1", "requirement_ref": "R1", "test_case_title": "T", "test_type": "Funzionale"}]


def _requirements_prompt(tmp_path, initiative=INITIATIVE) -> str:
    return build_requirements_prompt("# FILE: a.md\ntext", initiative, output_file=tmp_path / "p1.md")


def _outline(target=None, ui=None, known=()) -> str:
    return build_outline_prompt(REQUIREMENTS, ui, list(known), target, output_file=None)


def _detail(ui=None, corrections=()) -> str:
    return build_detail_prompt(CASES, REQUIREMENTS, ui, corrections, output_file=None)


# ------------------------------------------------------------------ prompt 1


def test_prompt1_receives_user_values_as_json_literals(tmp_path):
    prompt = _requirements_prompt(tmp_path)
    assert 'iniziativa_id: "1234567"' in prompt
    assert 'epic_id: "EP-100"' in prompt
    assert 'user_requirement_id: "XX12345"' in prompt


def test_prompt1_empty_epic_becomes_null(tmp_path):
    prompt = _requirements_prompt(tmp_path, InitiativeData(name="n", id="1", requirement_id="2"))
    assert "epic_id: null" in prompt
    assert 'iniziativa_id: "1"' in prompt


def test_prompt1_without_initiative_uses_null_not_raw_placeholders(tmp_path):
    prompt = _requirements_prompt(tmp_path, None)
    assert "iniziativa_id: null" in prompt
    assert "user_requirement_id: null" in prompt
    assert "{{" not in prompt.split("# FILE: a.md")[0]


def test_user_text_is_escaped_and_never_reexpanded(tmp_path):
    tricky = InitiativeData(id='Say "hi" {{EPIC_ID}} \\ end', epic="EP-9")
    prompt = _requirements_prompt(tmp_path, tricky)
    assert 'iniziativa_id: "Say \\"hi\\" {{EPIC_ID}} \\\\ end"' in prompt


def test_requirements_structure_has_user_requirement_id():
    text = REQUIREMENTS_PROMPT_TEMPLATE.read_text(encoding="utf-8")
    assert '"user_requirement_id": null' in text
    assert text.index('"epic_id": null') < text.index('"user_requirement_id": null')


# ------------------------------------------------------------------ fase A: elenco


def test_outline_template_has_both_mode_blocks():
    text = OUTLINE_PROMPT_TEMPLATE.read_text(encoding="utf-8")
    for mode in ("indicativo", "preciso"):
        assert "{{#MODALITA %s}}" % mode in text
    assert "MODALITÀ: INDICATIVO" in text
    assert "MODALITÀ: PRECISO" in text


def test_indicative_outline_has_only_the_impartial_rules():
    prompt = _outline(target=None)
    assert "MODALITÀ: INDICATIVO" in prompt
    assert "MODALITÀ: PRECISO" not in prompt
    assert "NUMERO_CASI_TEST: null" in prompt
    assert 'MODALITA_NUMERO_CASI_TEST: "indicativo"' in prompt


def test_precise_outline_has_the_story_target_as_a_number():
    prompt = _outline(target=7)
    assert "MODALITÀ: PRECISO" in prompt
    assert "MODALITÀ: INDICATIVO" not in prompt
    assert "NUMERO_CASI_TEST: 7" in prompt
    assert '"7"' not in prompt
    assert 'MODALITA_NUMERO_CASI_TEST: "preciso"' in prompt


@pytest.mark.parametrize("target", [0, -3])
def test_outline_without_a_positive_target_is_indicative(target):
    assert "MODALITÀ: INDICATIVO" in _outline(target=target)


def test_outline_contains_requirements_and_known_titles():
    prompt = _outline(known=["Titolo già usato"])
    assert '"ref":"R1"' in prompt
    assert "- Titolo già usato" in prompt
    assert "CASI GIÀ INDIVIDUATI" in prompt


def test_outline_without_known_titles_says_none():
    assert "Nessuno." in _outline()


def test_outline_ui_blocks_follow_the_spec():
    assert "SPECIFICA UI" not in _outline()
    with_ui = _outline(ui=UI)
    assert "USO DELLA SPECIFICA UI" in with_ui
    assert '"label":"Conferma"' in with_ui


def test_outline_requires_requirements():
    with pytest.raises(PromptBuildError):
        build_outline_prompt([], None, [], None, output_file=None)


# ------------------------------------------------------------------ fase B: step


def test_detail_contains_cases_requirements_and_rules():
    prompt = _detail()
    assert "CASI DA DETTAGLIARE" in prompt
    assert '"case_ref":"C1"' in prompt
    assert '"ref":"R1"' in prompt
    assert "GENERAZIONE DEGLI STEP" in prompt
    assert "VERIFICA ESTERNA" in prompt


def test_detail_ui_blocks_follow_the_spec():
    without = _detail()
    assert "SPECIFICA UI" not in without
    with_ui = _detail(ui=UI)
    assert "USO DELLA SPECIFICA UI" in with_ui
    assert "tra apici singoli" in with_ui


def test_detail_corrections_are_listed():
    prompt = _detail(corrections=["C1: manca lo Stato Base."])
    assert "CORREZIONI RICHIESTE" in prompt
    assert "- C1: manca lo Stato Base." in prompt
    assert "CORREZIONI RICHIESTE" not in _detail()


def test_detail_does_not_ask_the_model_for_traceability_fields():
    text = TEST_CASES_PROMPT_TEMPLATE.read_text(encoding="utf-8")
    for name in ("initiative_id", "epic_id", "user_requirement_id", "macro_area", "1234567"):
        assert name not in text


@pytest.mark.parametrize(
    "prompt_factory",
    [lambda: _outline(), lambda: _outline(target=4, ui=UI), lambda: _detail(), lambda: _detail(ui=UI)],
)
def test_no_marker_is_left_in_the_test_case_prompts(prompt_factory):
    assert not re.search(r"\{\{[#/]?[A-Z_]+[^}]*\}\}", prompt_factory())


def test_inline_blocks_are_rejected(tmp_path):
    template = tmp_path / "bad.md"
    template.write_text("Testo{{#SPECIFICA_UI}} in linea{{/SPECIFICA_UI}}.\n", encoding="utf-8")
    with pytest.raises(PromptBuildError, match="righe proprie"):
        _render(template, "Template di prova", with_ui=True)


# ------------------------------------------------------------------ modello


def test_test_case_model_accepts_the_extra_epic_id_field():
    """epic_id is in the test case JSON; the model ignores it, so the Excel export is unaffected."""
    case = TestCase.model_validate(
        {
            "initiative_id": "1234567",
            "epic_id": "EP-100",
            "requirement_use_case": "doc",
            "id3": "",
            "scenario_functionality": "s",
            "test_case_title": "t",
            "test_type": "Funzionale",
            "level": "",
            "estimated_duration": "00:20",
        }
    )
    assert case.initiative_id == "1234567"
    assert not hasattr(case, "epic_id")
