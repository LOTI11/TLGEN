"""Test list generation in several requests (fake model, no Gemini calls)."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dev.import_test_cases_xlsm import load_test_cases  # noqa: E402
from models.TestCase import TestCase  # noqa: E402
from models.llm_schemas import DetailCase, CaseKind  # noqa: E402
from services.json_generation import JsonGenerationError  # noqa: E402
from services.llm_types import LlmResult, TruncatedResponseError  # noqa: E402
from services.prompt_builder import InitiativeData  # noqa: E402
from services.requirements_extraction import extract_requirements  # noqa: E402
import services.test_case_generation as generation  # noqa: E402
from services.test_case_generation import (  # noqa: E402
    allocate_targets,
    check_standards,
    generate_test_list,
    plan_user_stories,
    ui_for_story,
)

INITIATIVE = InitiativeData(name="Gestione abbonamento", id="111", epic="onp-222", requirement_id="333")


def _requirement(source_id, title, criteria=1, confluence_id=None):
    return {
        "source": "CONFLUENCE",
        "source_id": source_id,
        "iniziativa_id": "111",
        "epic_id": "onp-222",
        "user_requirement_id": "333",
        "jira_id": None,
        "confluence_id": confluence_id,
        "title": title,
        "description": f"Descrizione di {title}",
        "acceptance_criteria": [f"criterio {i}" for i in range(criteria)],
        "business_rules": [],
        "systems": [],
        "platforms": ["APP"],
        "source_reference": None,
    }


REQUIREMENTS = {
    "source_files": [{"file_name": "ONP-1 Cambio piano.md"}, {"file_name": "ONP-2 Disattiva.md"}],
    "requirements": [
        _requirement("ONP-1 Cambio piano.md", "Selezione piano", criteria=3, confluence_id="CONF-9"),
        _requirement("ONP-2 Disattiva.md", "Disattivazione"),
        _requirement("ONP-1 Cambio piano.md", "Riepilogo piano"),
    ],
}


def _section(prompt: str, title: str):
    match = re.search(re.escape(title) + r"\n=+\n\n(.*)\n", prompt)
    return json.loads(match.group(1)) if match else None


def _steps(test_type: str, internal_ref: bool = False):
    steps = [
        ("Attività Preliminari e/o Precondizioni", "Utente con abbonamento attivo"),
        ("Stato Base", "Post-login"),
        ("Azione", "Tap sulla CTA 'Cambia piano'" + (" su S3" if internal_ref else "")),
        ("Verifica interna", "Verificare la schermata 'Riepilogo'"),
    ]
    if test_type == "Integrato":
        steps.append(("Verifica esterna", "azione_servizio_ver.esterna"))
    return [
        {
            "step_number": 10 + i,  # wrong on purpose: the code renumbers 1..n
            "step_type": kind,
            "step_name": f"Step {i}",
            "actions_and_data": action,
            "expected_result": "Risultato verificabile",
        }
        for i, (kind, action) in enumerate(steps)
    ]


class FakeModel:
    """Answers like Gemini would, based on the kind of prompt (case list or steps)."""

    def __init__(self, cases_per_requirement=1, test_type="Funzionale"):
        self.cases_per_requirement = cases_per_requirement
        self.test_type = test_type
        self.prompts: list[str] = []
        self.truncate_outline_once = False
        self.truncate_detail_over = None  # truncate detail requests with more cases than this
        self.bad_steps_times = 0  # first N detail answers have an internal reference
        self.skip_refs: set[str] = set()  # requirement refs left without cases (first time)

    def generate_json(self, prompt, *, files=(), schema=None, thinking_budget=None, on_status=None):
        self.prompts.append(prompt)
        if "FASE 1 di 2" in prompt:
            requirements = _section(prompt, "REQUISITI DELLA USER STORY")
            if self.truncate_outline_once and len(requirements) > 1:
                self.truncate_outline_once = False
                raise TruncatedResponseError(LlmResult("{", "MAX_TOKENS"))
            cases = [
                {
                    "requirement_ref": r["ref"],
                    "test_case_title": f"{r['title']} caso {n}",
                    "scenario_test_case": f"Scenario {r['title']} {n}",
                    "test_type": self.test_type,
                    "covered_conditions": r["acceptance_criteria"],
                }
                for r in requirements
                if r["ref"] not in self.skip_refs
                for n in range(1, self.cases_per_requirement + 1)
            ]
            self.skip_refs = set()
            return LlmResult(json.dumps({"test_cases": cases}))

        cases = _section(prompt, "CASI DA DETTAGLIARE")
        if self.truncate_detail_over is not None and len(cases) > self.truncate_detail_over:
            raise TruncatedResponseError(LlmResult("{", "MAX_TOKENS"))
        bad = self.bad_steps_times > 0
        self.bad_steps_times -= 1
        return LlmResult(
            json.dumps(
                {
                    "test_cases": [
                        {
                            "case_ref": c["case_ref"],
                            "description_notes": f"Scopo di {c['test_case_title']}",
                            "steps": _steps(c["test_type"], internal_ref=bad),
                        }
                        for c in cases
                    ]
                }
            )
        )

    def kinds(self):
        return ["elenco" if "FASE 1 di 2" in p else "step" for p in self.prompts]


def _generate(tmp_path, model, requirements=REQUIREMENTS, ui=None, target=None, mode="indicativo"):
    return generate_test_list(
        requirements,
        ui,
        INITIATIVE,
        model,
        target,
        mode,
        json_file=tmp_path / "test_cases.json",
        prompt_dir=tmp_path / "prompts",
        raw_dir=tmp_path / "raw",
        partial_file=tmp_path / "partial.json",
    )


# ------------------------------------------------------------------ piano


def test_requirements_are_grouped_by_user_story_in_order():
    stories = plan_user_stories(REQUIREMENTS)
    assert [s.label for s in stories] == ["ONP-1 Cambio piano", "ONP-2 Disattiva"]
    assert [len(s.requirements) for s in stories] == [2, 1]
    assert [r["ref"] for r in stories[0].payload()] == ["R1", "R2"]
    assert "iniziativa_id" not in stories[0].payload()[0]  # the model does not need them


def test_precise_mode_splits_the_number_by_complexity():
    stories = plan_user_stories(REQUIREMENTS)
    allocate_targets(stories, 10, "preciso")
    assert sum(s.target for s in stories) == 10
    assert stories[0].target > stories[1].target >= 1
    allocate_targets(stories, 10, "indicativo")
    assert [s.target for s in stories] == [None, None]


def test_ui_screens_are_filtered_by_user_story_and_compacted():
    ui = {
        "screens": [
            {"screen_id": "S1", "name": "Piani", "state": "default",
             "requirement_source_ids": ["ONP-1 Cambio piano.md"], "source_file": "05.pdf", "page": 2,
             "elements": [{"label": "Continua", "notes": None}],
             "navigation": [{"trigger_label": "Continua", "target_screen_id": "S2"},
                            {"trigger_label": "Esci", "target_screen_id": "S9"}]},
            {"screen_id": "S2", "name": "Riepilogo", "state": "errore", "requirement_source_ids": []},
            {"screen_id": "S3", "name": "Disattiva", "requirement_source_ids": ["ONP-2 Disattiva"]},
            {"screen_id": "S9", "name": "Home", "requirement_source_ids": []},
        ],
        "flows": [{"name": "Cambio", "screen_ids": ["S1", "S2"],
                   "requirement_source_ids": ["onp-1 cambio piano"], "description": "x"}],
    }
    first = ui_for_story(ui, "ONP-1 Cambio piano.md")
    assert [s["name"] for s in first["screens"]] == ["Piani", "Riepilogo"]  # S2 through the flow
    assert first["screens"][0] == {
        "name": "Piani",
        "state": "default",
        "elements": [{"label": "Continua"}],
        "navigation": [
            {"trigger_label": "Continua", "target_screen": "Riepilogo (errore)"},
            {"trigger_label": "Esci", "target_screen": "Home"},  # screen outside the story
        ],
    }
    assert first["flows"] == [{"name": "Cambio", "screens": ["Piani", "Riepilogo (errore)"], "description": "x"}]
    assert not re.search(r"\bS\d+\b", json.dumps(first))  # no screen id reaches the model
    assert [s["name"] for s in ui_for_story(ui, "ONP-2 Disattiva.md")["screens"]] == ["Disattiva"]
    assert ui_for_story(ui, "ONP-9 Altro.md") is None
    assert ui_for_story(None, "ONP-1 Cambio piano.md") is None


# ------------------------------------------------------------------ generazione


def test_full_run_fills_traceability_from_the_requirement(tmp_path):
    model = FakeModel(test_type="Funzionale")
    report = _generate(tmp_path, model)
    cases = report.data["test_cases"]
    assert len(cases) == 3
    assert model.kinds() == ["elenco", "step", "elenco", "step"]
    first = cases[0]
    assert first["initiative_id"] == "111"
    assert first["user_requirement_id"] == "333"
    assert first["epic_id"] == "onp-222"
    assert first["macro_area"] == "Gestione abbonamento"
    assert first["requirement_use_case"] == "ONP-1 Cambio piano"
    assert first["id3"] == "CONF-9"
    assert cases[1]["id3"] == ""
    assert first["scenario_functionality"] == "Scenario"
    assert first["estimated_duration"] == "00:20"
    assert first["level"] == ""
    assert first["test_case_macro_funzionalita"] == "Selezione piano"
    assert first["description_notes"] == "Scopo di Selezione piano caso 1"
    assert [s["step_number"] for s in first["steps"]] == [1, 2, 3, 4]
    assert report.warnings == []


def test_result_is_accepted_by_the_excel_export_loader(tmp_path):
    _generate(tmp_path, FakeModel(test_type="Integrato"))
    loaded = load_test_cases(tmp_path / "test_cases.json")
    assert len(loaded) == 3
    assert all(isinstance(c, TestCase) for c in loaded)
    assert loaded[0].steps[-1].step_type.value == "Verifica esterna"


def test_partial_file_and_debug_files_are_written(tmp_path):
    _generate(tmp_path, FakeModel())
    assert len(json.loads((tmp_path / "partial.json").read_text(encoding="utf-8"))["test_cases"]) == 3
    assert len(list((tmp_path / "prompts").glob("*.md"))) == 4
    assert len(list((tmp_path / "raw").glob("*.json"))) == 4


def test_step_prompts_name_requirements_by_title_not_by_ref(tmp_path):
    model = FakeModel()
    _generate(tmp_path, model)
    detail = next(p for p in model.prompts if "FASE 2 di 2" in p)
    cases = _section(detail, "CASI DA DETTAGLIARE")
    assert cases[0]["requirement_title"] == "Selezione piano"
    assert "requirement_ref" not in cases[0]
    assert all("ref" not in r for r in _section(detail, "REQUISITI DELLA USER STORY"))


def test_steps_are_requested_in_batches(tmp_path):
    model = FakeModel(cases_per_requirement=6)  # 12 cases for the first user story
    report = _generate(tmp_path, model)
    assert len(report.data["test_cases"]) == 18
    sizes = [len(_section(p, "CASI DA DETTAGLIARE")) for p in model.prompts if "FASE 2 di 2" in p]
    assert sizes == [5, 5, 2, 5, 1]


def test_truncated_step_answers_are_split_until_they_fit(tmp_path):
    model = FakeModel(cases_per_requirement=3)
    model.truncate_detail_over = 2
    report = _generate(tmp_path, model)
    assert len(report.data["test_cases"]) == 9
    assert all(c["steps"] for c in report.data["test_cases"])


def test_truncated_case_list_is_split_by_requirement(tmp_path):
    model = FakeModel()
    model.truncate_outline_once = True
    report = _generate(tmp_path, model)
    assert len(report.data["test_cases"]) == 3
    assert model.kinds()[:3] == ["elenco", "elenco", "elenco"]


def test_non_compliant_cases_are_regenerated_with_the_errors(tmp_path):
    model = FakeModel()
    model.bad_steps_times = 1  # the first answer mentions "S3"
    report = _generate(tmp_path, model)
    fixes = [p for p in model.prompts if "CORREZIONI RICHIESTE" in p]
    assert fixes and "riferimento interno ('S3')" in fixes[0]
    assert report.warnings == []
    assert "S3" not in json.dumps(report.data)


def test_cases_still_wrong_after_the_retries_are_kept_with_a_warning(tmp_path):
    model = FakeModel()
    model.bad_steps_times = 100
    report = _generate(tmp_path, model)
    assert len(report.data["test_cases"]) == 3
    assert len(report.warnings) == 3
    assert "riferimento interno" in report.warnings[0]


def test_uncovered_requirements_get_their_own_case_list(tmp_path):
    model = FakeModel()
    model.skip_refs = {"R2"}  # the first case list forgets the second requirement
    report = _generate(tmp_path, model)
    assert len(report.data["test_cases"]) == 3
    follow_up = model.prompts[1]
    assert "FASE 1 di 2" in follow_up
    assert [r["ref"] for r in _section(follow_up, "REQUISITI DELLA USER STORY")] == ["R2"]
    assert "- Selezione piano caso 1" in follow_up  # no duplicates of what exists


def test_precise_mode_passes_the_story_target_to_the_case_list(tmp_path):
    model = FakeModel()
    _generate(tmp_path, model, target=5, mode="preciso")
    outline_prompts = [p for p in model.prompts if "FASE 1 di 2" in p]
    targets = [int(re.search(r"NUMERO_CASI_TEST: (\d+)", p).group(1)) for p in outline_prompts]
    assert sum(targets) == 5


def test_only_the_story_screens_reach_its_prompts(tmp_path):
    ui = {
        "screens": [
            {"screen_id": "S1", "name": "Piani", "requirement_source_ids": ["ONP-1 Cambio piano.md"]},
            {"screen_id": "S9", "name": "Disattiva", "requirement_source_ids": ["ONP-2 Disattiva.md"]},
        ]
    }
    model = FakeModel()
    _generate(tmp_path, model, ui=ui)
    first_story = model.prompts[0]
    assert '"name":"Piani"' in first_story and '"name":"Disattiva"' not in first_story
    assert "USO DELLA SPECIFICA UI" in first_story


def test_wrong_case_refs_are_asked_again(tmp_path):
    model = FakeModel()
    original = model.generate_json
    answers = {"n": 0}

    def flaky(prompt, **kwargs):
        result = original(prompt, **kwargs)
        if "FASE 2 di 2" in prompt and answers["n"] == 0:
            answers["n"] += 1
            return LlmResult(json.dumps({"test_cases": []}))
        return result

    model.generate_json = flaky
    report = _generate(tmp_path, model)
    assert len(report.data["test_cases"]) == 3


def test_several_requirement_refs_keep_the_first_valid_one(tmp_path):
    model = FakeModel()
    original = model.generate_json

    def multi_ref(prompt, **kwargs):
        result = original(prompt, **kwargs)
        if "FASE 1 di 2" in prompt:
            data = json.loads(result.text)
            for case in data["test_cases"]:
                case["requirement_ref"] = f"R9, {case['requirement_ref']} e R1"  # R9 does not exist
            return LlmResult(json.dumps(data))
        return result

    model.generate_json = multi_ref
    report = _generate(tmp_path, model)
    titles = [c["test_case_macro_funzionalita"] for c in report.data["test_cases"]]
    assert titles == ["Selezione piano", "Riepilogo piano", "Disattivazione"]


def test_a_failing_user_story_does_not_stop_the_others(tmp_path):
    model = FakeModel()
    original = model.generate_json

    def broken_second_story(prompt, **kwargs):
        if "Descrizione di Disattivazione" in prompt:  # data of the second user story only
            return LlmResult("not json")
        return original(prompt, **kwargs)

    model.generate_json = broken_second_story
    report = _generate(tmp_path, model)
    assert len(report.data["test_cases"]) == 2  # first user story only
    assert report.failed_stories == ["ONP-2 Disattiva"]
    assert report.warnings[0].startswith("USER STORY NON GENERATA: ONP-2 Disattiva")
    assert len(json.loads((tmp_path / "test_cases.json").read_text(encoding="utf-8"))["test_cases"]) == 2


def test_no_requirements_is_an_error(tmp_path):
    with pytest.raises(JsonGenerationError):
        _generate(tmp_path, FakeModel(), requirements={"requirements": []})


# ------------------------------------------------------------------ standard


def _case(steps, notes="Scopo"):
    return DetailCase.model_validate({"case_ref": "C1", "description_notes": notes, "steps": steps})


def test_compliant_case_has_no_issues():
    assert check_standards(_case(_steps("Funzionale")), CaseKind.FUNZIONALE) == []
    assert check_standards(_case(_steps("Integrato")), CaseKind.INTEGRATO) == []


def test_external_check_must_match_the_test_type():
    assert any("Integrato" in i for i in check_standards(_case(_steps("Funzionale")), CaseKind.INTEGRATO))
    assert any("Funzionale" in i for i in check_standards(_case(_steps("Integrato")), CaseKind.FUNZIONALE))


def test_order_and_required_step_types():
    steps = _steps("Funzionale")
    issues = check_standards(_case([steps[1], steps[0], steps[2]]), CaseKind.FUNZIONALE)
    assert any("primo step" in i for i in issues)
    assert any("Verifica interna" in i for i in issues)
    double_base = [steps[0], steps[1], steps[1], steps[2], steps[3]]
    assert any("esattamente uno" in i for i in check_standards(_case(double_base), CaseKind.FUNZIONALE))


def test_empty_fields_and_internal_refs_are_reported():
    steps = _steps("Funzionale")
    steps[2]["expected_result"] = " "
    steps[3]["actions_and_data"] = "Verificare la schermata P2-S14"
    issues = check_standards(_case(steps, notes=""), CaseKind.FUNZIONALE)
    assert "description_notes è vuoto." in issues
    assert "step 3: expected_result è vuoto." in issues
    assert any("P2-S14" in i for i in issues)
    assert check_standards(_case([]), CaseKind.FUNZIONALE) == ["il caso non ha step."]
    notes = check_standards(_case(_steps("Funzionale"), notes="Come da requisito R1."), CaseKind.FUNZIONALE)
    assert any("description_notes" in i and "'R1'" in i for i in notes)


# ------------------------------------------------------------------ requisiti


class FakeRequirementsModel:
    def __init__(self, truncate_over=None):
        self.truncate_over = truncate_over
        self.prompts = []

    def generate_json(self, prompt, *, files=(), schema=None, thinking_budget=None, on_status=None):
        self.prompts.append(prompt)
        names = re.findall(r"# FILE: (.+)", prompt)
        if self.truncate_over is not None and len(names) > self.truncate_over:
            raise TruncatedResponseError(LlmResult("{", "MAX_TOKENS"))
        return LlmResult(
            json.dumps(
                {
                    "source_files": [{"file_name": n} for n in names],
                    "requirements": [_requirement(n, f"Req {n}") for n in names],
                }
            )
        )


def _documents(*names):
    return [f"\n# FILE: {n}\n\ntesto\n\n# FINE FILE: {n}\n" for n in names]


def test_requirements_in_one_request(tmp_path):
    model = FakeRequirementsModel()
    result = extract_requirements(
        _documents("a.md", "b.md"), INITIATIVE, model,
        raw_file=tmp_path / "raw.txt", json_file=tmp_path / "req.json", prompt_file=None,
    )
    assert len(model.prompts) == 1
    assert len(result.data["requirements"]) == 2


def test_truncated_requirements_are_split_by_documents(tmp_path):
    model = FakeRequirementsModel(truncate_over=1)
    result = extract_requirements(
        _documents("a.md", "b.md", "c.md"), INITIATIVE, model,
        raw_file=tmp_path / "raw.txt", json_file=tmp_path / "req.json", prompt_file=None,
    )
    assert result.parts == 3
    assert [f["file_name"] for f in result.data["source_files"]] == ["a.md", "b.md", "c.md"]
    assert len(result.data["requirements"]) == 3
    assert json.loads((tmp_path / "req.json").read_text(encoding="utf-8")) == result.data


def test_module_constants_keep_answers_far_from_the_limit():
    # 5 cases x 25 steps x ~110 tokens + reasoning budget must stay under 65,535 tokens.
    assert generation.DETAIL_BATCH_SIZE * 25 * 110 + generation.DETAIL_THINKING_BUDGET < 65535 / 2
