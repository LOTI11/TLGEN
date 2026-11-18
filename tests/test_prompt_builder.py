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
    REQUIREMENTS_PROMPT_TEMPLATE,
    TEST_CASES_PROMPT_TEMPLATE,
    InitiativeData,
    build_requirements_prompt,
    build_test_cases_prompt,
)

# Placeholders the builders are responsible for (NUMERO_CASI_TEST is not one of them).
FILLED_PLACEHOLDERS = ("INIZIATIVA_ID", "EPIC_ID", "USER_REQUIREMENT_ID", "NOME_INIZIATIVA")

INITIATIVE = InitiativeData(
    name="Gestione abbonamento", id="1234567", epic="EP-100", requirement_id="XX12345"
)


def _requirements_prompt(tmp_path, initiative=INITIATIVE) -> str:
    return build_requirements_prompt("# FILE: a.md\ntext", initiative, output_file=tmp_path / "p1.md")


@pytest.fixture
def requirements_json(tmp_path) -> Path:
    path = tmp_path / "requirements.json"
    path.write_text('{"requirements": []}', encoding="utf-8")
    return path


def _test_cases_prompt(tmp_path, requirements_json, initiative=INITIATIVE) -> str:
    return build_test_cases_prompt(
        initiative, requirements_json_file=requirements_json, output_file=tmp_path / "p2.md"
    )


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


def test_prompt2_receives_initiative_name(tmp_path, requirements_json):
    prompt = _test_cases_prompt(tmp_path, requirements_json)
    assert 'NOME_INIZIATIVA: "Gestione abbonamento"' in prompt
    assert prompt.endswith('{"requirements": []}')


def test_prompt2_missing_name_becomes_null(tmp_path, requirements_json):
    prompt = _test_cases_prompt(tmp_path, requirements_json, None)
    assert "NOME_INIZIATIVA: null" in prompt


def test_user_text_is_escaped_and_never_reexpanded(tmp_path, requirements_json):
    tricky = InitiativeData(name='Say "hi" {{EPIC_ID}} \\ end', epic="EP-9")
    prompt = _test_cases_prompt(tmp_path, requirements_json, tricky)
    assert 'NOME_INIZIATIVA: "Say \\"hi\\" {{EPIC_ID}} \\\\ end"' in prompt


@pytest.mark.parametrize("template", [REQUIREMENTS_PROMPT_TEMPLATE, TEST_CASES_PROMPT_TEMPLATE])
def test_no_filled_placeholder_is_left_in_the_final_prompts(tmp_path, requirements_json, template):
    if template == REQUIREMENTS_PROMPT_TEMPLATE:
        prompt = _requirements_prompt(tmp_path)
    else:
        prompt = _test_cases_prompt(tmp_path, requirements_json)
    leftovers = [n for n in re.findall(r"\{\{([A-Z_]+)\}\}", prompt) if n in FILLED_PLACEHOLDERS]
    assert leftovers == []


def test_requirements_structure_has_user_requirement_id():
    text = REQUIREMENTS_PROMPT_TEMPLATE.read_text(encoding="utf-8")
    assert '"user_requirement_id": null' in text
    assert text.index('"epic_id": null') < text.index('"user_requirement_id": null')


def test_test_case_prompt_has_no_hardcoded_ids_and_has_epic():
    text = TEST_CASES_PROMPT_TEMPLATE.read_text(encoding="utf-8")
    assert "1234567" not in text
    assert "XX12345" not in text
    assert text.count('"epic_id": null') == 2  # input structure and output structure
    assert text.count('"user_requirement_id": null') == 2


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
