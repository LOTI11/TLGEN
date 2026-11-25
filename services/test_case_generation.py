"""Generazione della test list in più richieste, con risposte sempre complete.

Una sola risposta del modello non può contenere un'intera test list (massimo di
circa 65.000 token in uscita, ragionamento incluso). Il lavoro è quindi diviso
dal codice:

1. i requisiti sono raggruppati per user story (``source_id``), ognuna con le sole
   schermate UI collegate;
2. fase A: per ogni user story il modello individua l'elenco dei casi (senza step);
   se un requisito resta senza casi viene richiesto un elenco solo per quello;
3. fase B: gli step vengono generati a gruppi di pochi casi;
4. ogni caso è controllato rispetto allo standard (tipi di step, ordine, campi
   vuoti, riferimenti interni); i casi non conformi vengono rigenerati con
   l'elenco degli errori;
5. i campi di tracciabilità sono compilati dal codice a partire dal requisito,
   secondo le regole del prompt (iniziativa, epica, requisito utente, macro area,
   use case, id3, scenario, durata).

Ogni risposta troncata viene divisa a metà (``split_on_truncation``): non arriva
mai all'export un caso incompleto.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from models.TestCase import StepType, TestCase
from models.llm_schemas import DetailCase, DetailResponse, OutlineCase, OutlineResponse, CaseKind
from services.json_generation import (
    DATA_INPUT,
    TEST_CASES_JSON_FILE,
    JsonGenerationError,
    request_json,
    save_json,
    split_on_truncation,
)
from services.llm_types import JsonLlmClient, StatusCallback
from services.prompt_builder import (
    COUNT_MODE_PRECISE,
    TEST_CASES_PROMPT_DIR,
    InitiativeData,
    build_detail_prompt,
    build_outline_prompt,
)

OUTLINE_THINKING_BUDGET = 8192
DETAIL_THINKING_BUDGET = 6144
# Casi per richiesta nella fase B: circa 5 x 25 step x 110 token = 14.000 token,
# molto sotto il massimo in uscita anche con il ragionamento.
DETAIL_BATCH_SIZE = 5
# Nuovi tentativi per un caso che non rispetta lo standard.
MAX_FIX_ATTEMPTS = 2

TEST_CASES_RAW_DIR = DATA_INPUT / "testCasesRaw"
TEST_CASES_PARTIAL_FILE = DATA_INPUT / "jsonAI" / "test_cases_partial.json"

# Valori fissi del prompt (sezione TRACCIABILITÀ REQUISITO -> TEST CASE).
SCENARIO_FUNCTIONALITY = "Scenario"
ESTIMATED_DURATION = "00:20"

_REQUIREMENT_FIELDS = (
    "jira_id",
    "confluence_id",
    "title",
    "description",
    "acceptance_criteria",
    "business_rules",
    "systems",
    "platforms",
    "source_reference",
)
_SCREEN_FIELDS = ("screen_id", "name", "state", "purpose", "elements", "messages", "navigation")
_INTERNAL_REF = re.compile(r"\b(?:P\d+-)?[RCS]\d{1,3}\b")


# ------------------------------------------------------------------ piano


@dataclass
class UserStory:
    source_id: str
    requirements: list[dict[str, Any]]  # requisiti originali, nell'ordine del JSON
    ui_spec: dict[str, Any] | None = None
    target: int | None = None  # casi richiesti (solo modalità preciso)

    @property
    def label(self) -> str:
        return use_case_name(self.source_id)

    @property
    def weight(self) -> int:
        return sum(
            1 + len(r.get("acceptance_criteria") or []) + len(r.get("business_rules") or [])
            for r in self.requirements
        )

    def ref(self, index: int) -> str:
        return f"R{index + 1}"

    def payload(
        self, indexes: Sequence[int] | None = None, with_ref: bool = True
    ) -> list[dict[str, Any]]:
        """Requisiti come li vede il modello: campi funzionali (niente ID utente).

        ``ref`` (R1, R2, ...) serve solo nella fase A per collegare i casi ai requisiti;
        nella fase B non viene passato, altrimenti il modello lo cita nei testi.
        """
        chosen = range(len(self.requirements)) if indexes is None else indexes
        return [
            {
                **({"ref": self.ref(i)} if with_ref else {}),
                **{k: self.requirements[i].get(k) for k in _REQUIREMENT_FIELDS},
            }
            for i in chosen
        ]


def use_case_name(source_id: str) -> str:
    """source_id senza estensione del file (regola di requirement_use_case)."""
    name = (source_id or "").strip()
    return re.sub(r"\.(md|pdf|docx|json|txt)$", "", name, flags=re.IGNORECASE)


def _story_key(source_id: str) -> str:
    return re.sub(r"\s+", " ", use_case_name(source_id)).strip().casefold()


def _clean(value: Any) -> Any:
    """Toglie valori vuoti (null, "", []) per non sprecare token."""
    if isinstance(value, dict):
        cleaned = {k: _clean(v) for k, v in value.items()}
        return {k: v for k, v in cleaned.items() if v not in (None, "", [], {})}
    if isinstance(value, list):
        return [c for c in (_clean(v) for v in value) if c not in (None, "", [], {})]
    return value


def _screen_label(screen: Mapping[str, Any]) -> str:
    name = str(screen.get("name") or "").strip() or "Schermata senza nome"
    state = str(screen.get("state") or "").strip()
    return f"{name} ({state})" if state and state.casefold() != "default" else name


def ui_for_story(ui_spec: Mapping[str, Any] | None, source_id: str) -> dict[str, Any] | None:
    """Schermate e flussi collegati alla user story, in forma compatta; None se nessuno.

    Gli screen_id non vengono passati al modello (finirebbero negli step): ogni
    riferimento a una schermata, anche nella navigazione e nei flussi, diventa il
    suo nome (con lo stato, se non è quello di default).
    """
    if not ui_spec:
        return None
    key = _story_key(source_id)
    all_screens = ui_spec.get("screens") or []
    labels = {s.get("screen_id"): _screen_label(s) for s in all_screens}

    def linked(item: Mapping[str, Any]) -> bool:
        return any(_story_key(s) == key for s in item.get("requirement_source_ids") or [])

    flows = [f for f in ui_spec.get("flows") or [] if linked(f)]
    flow_screens = {s for f in flows for s in f.get("screen_ids") or []}
    screens = []
    for screen in all_screens:
        if not (linked(screen) or screen.get("screen_id") in flow_screens):
            continue
        item = {k: screen.get(k) for k in _SCREEN_FIELDS if k not in ("screen_id", "navigation")}
        item["navigation"] = [
            {
                "trigger_label": nav.get("trigger_label"),
                "target_screen": labels.get(nav.get("target_screen_id"))
                or nav.get("target_description"),
            }
            for nav in screen.get("navigation") or []
        ]
        screens.append(item)
    if not screens:
        return None
    return _clean(
        {
            "screens": screens,
            "flows": [
                {
                    "name": f.get("name"),
                    "screens": [labels.get(s, s) for s in f.get("screen_ids") or []],
                    "description": f.get("description"),
                }
                for f in flows
            ],
        }
    )


def plan_user_stories(
    requirements_data: Mapping[str, Any], ui_spec: Mapping[str, Any] | None = None
) -> list[UserStory]:
    """Raggruppa i requisiti per user story, nell'ordine in cui compaiono."""
    stories: dict[str, UserStory] = {}
    for requirement in requirements_data.get("requirements") or []:
        source_id = str(requirement.get("source_id") or "senza user story")
        story = stories.setdefault(_story_key(source_id), UserStory(source_id, []))
        story.requirements.append(requirement)
    for story in stories.values():
        story.ui_spec = ui_for_story(ui_spec, story.source_id)
    return list(stories.values())


def allocate_targets(stories: Sequence[UserStory], total: int | None, mode: str) -> None:
    """Modalità preciso: ripartisce ``total`` tra le user story in base alla complessità.

    Metodo dei resti più grandi (la somma è sempre ``total``); se il numero lo
    consente ogni user story ha almeno un caso.
    """
    for story in stories:
        story.target = None
    if mode != COUNT_MODE_PRECISE or not total or total < 1 or not stories:
        return
    minimum = 1 if total >= len(stories) else 0
    remaining = total - minimum * len(stories)
    weights = [s.weight for s in stories]
    shares = [remaining * w / sum(weights) for w in weights]
    counts = [minimum + int(share) for share in shares]
    leftover = total - sum(counts)
    order = sorted(range(len(stories)), key=lambda i: shares[i] - int(shares[i]), reverse=True)
    for i in order[:leftover]:
        counts[i] += 1
    for story, count in zip(stories, counts):
        story.target = count


# ------------------------------------------------------------------ controlli


def check_standards(case: DetailCase, test_type: CaseKind) -> list[str]:
    """Regole dello standard verificabili dal codice; lista vuota = caso conforme."""
    issues: list[str] = []
    steps = case.steps
    if not steps:
        return ["il caso non ha step."]
    types = [s.step_type for s in steps]

    if not case.description_notes.strip():
        issues.append("description_notes è vuoto.")
    elif _INTERNAL_REF.search(case.description_notes):
        issues.append(
            "description_notes contiene un riferimento interno "
            f"('{_INTERNAL_REF.search(case.description_notes).group(0)}'); "
            "cita il requisito con il suo titolo."
        )
    if types[0] != StepType.ATTIVITA_PRELIMINARI_PRECONDIZIONI:
        issues.append('il primo step deve essere "Attività Preliminari e/o Precondizioni".')
    if types.count(StepType.STATO_BASE) != 1:
        issues.append('deve esserci esattamente uno step "Stato Base".')
    else:
        base = types.index(StepType.STATO_BASE)
        if any(t != StepType.ATTIVITA_PRELIMINARI_PRECONDIZIONI for t in types[:base]):
            issues.append('prima dello "Stato Base" sono ammesse solo precondizioni.')
        if StepType.ATTIVITA_PRELIMINARI_PRECONDIZIONI in types[base + 1 :]:
            issues.append('le precondizioni devono precedere lo "Stato Base".')
    if StepType.AZIONE not in types:
        issues.append('manca almeno uno step "Azione".')
    if StepType.VERIFICA_INTERNA not in types:
        issues.append('manca almeno uno step "Verifica interna".')
    has_external = StepType.VERIFICA_ESTERNA in types
    if test_type == CaseKind.INTEGRATO and not has_external:
        issues.append('il test è Integrato: serve almeno uno step "Verifica esterna".')
    if test_type == CaseKind.FUNZIONALE and has_external:
        issues.append('il test è Funzionale: non sono ammessi step "Verifica esterna".')

    for number, step in enumerate(steps, start=1):
        for name in ("step_name", "actions_and_data", "expected_result"):
            text = getattr(step, name)
            if not text.strip():
                issues.append(f"step {number}: {name} è vuoto.")
            elif _INTERNAL_REF.search(text):
                issues.append(
                    f"step {number}: {name} contiene un riferimento interno "
                    f"('{_INTERNAL_REF.search(text).group(0)}'); usa il nome della schermata."
                )
    return issues


# ------------------------------------------------------------------ generazione


@dataclass
class _Case:
    """Un caso durante la generazione."""

    ref: str  # C1, C2, ... (univoco nella user story)
    requirement_index: int
    outline: OutlineCase
    detail: DetailCase | None = None
    issues: list[str] = field(default_factory=list)

    def payload(self, story: UserStory) -> dict[str, Any]:
        return {
            "case_ref": self.ref,
            "requirement_title": story.requirements[self.requirement_index].get("title"),
            "test_case_title": self.outline.test_case_title,
            "scenario_test_case": self.outline.scenario_test_case,
            "test_type": self.outline.test_type.value,
            "covered_conditions": self.outline.covered_conditions,
        }


@dataclass
class GenerationReport:
    data: dict[str, Any]
    text: str
    stories: int
    calls: int
    warnings: list[str]
    failed_stories: list[str] = field(default_factory=list)


class TestListGenerator:
    """Esegue il piano: fase A e fase B per ogni user story, poi unisce e salva."""

    __test__ = False  # not a pytest class

    def __init__(
        self,
        llm: JsonLlmClient,
        initiative: InitiativeData,
        on_status: StatusCallback | None = None,
        prompt_dir: Path | None = TEST_CASES_PROMPT_DIR,
        raw_dir: Path | None = TEST_CASES_RAW_DIR,
        partial_file: Path | None = TEST_CASES_PARTIAL_FILE,
    ) -> None:
        self.llm = llm
        self.initiative = initiative
        self.on_status = on_status
        self.prompt_dir = prompt_dir
        self.raw_dir = raw_dir
        self.partial_file = partial_file
        self.calls = 0
        self.warnings: list[str] = []
        for directory in (prompt_dir, raw_dir):
            if directory is not None and directory.is_dir():
                for old in directory.glob("*.*"):
                    old.unlink()

    # -------------------------------------------------------------- utilità

    def _status(self, message: str) -> None:
        if self.on_status:
            self.on_status(message)

    def _files(self, story_number: int, step: str) -> tuple[Path | None, Path | None]:
        self.calls += 1
        name = f"{self.calls:03d}_US{story_number:02d}_{step}"
        prompt = self.prompt_dir / f"{name}.md" if self.prompt_dir else None
        raw = self.raw_dir / f"{name}.json" if self.raw_dir else None
        return prompt, raw

    # -------------------------------------------------------------- fase A

    def _outline(
        self,
        story: UserStory,
        number: int,
        indexes: Sequence[int],
        known_titles: Sequence[str],
        target: int | None,
    ) -> list[tuple[int, OutlineCase]]:
        refs = {story.ref(i): i for i in indexes}

        def run(subset: Sequence[int]) -> list[tuple[int, OutlineCase]]:
            subset_target = (
                max(1, round(target * len(subset) / len(indexes))) if target else None
            )
            prompt_file, raw_file = self._files(number, "elenco")
            prompt = build_outline_prompt(
                story.payload(subset),
                story.ui_spec,
                known_titles,
                subset_target,
                output_file=prompt_file,
            )
            allowed = {story.ref(i) for i in subset}
            parsed: list[OutlineCase] = []

            def check(data: Any) -> None:
                try:
                    response = OutlineResponse.model_validate(data)
                except ValidationError as exc:
                    raise JsonGenerationError(f"elenco non valido: {exc}") from exc
                wrong = []
                for case in response.test_cases:
                    # "R1, R2" (more requirements): the first valid one is the main requirement.
                    valid = [r for r in re.findall(r"R\d+", case.requirement_ref) if r in allowed]
                    if valid:
                        case.requirement_ref = valid[0]
                    else:
                        wrong.append(case.requirement_ref)
                if wrong:
                    raise JsonGenerationError(f"requirement_ref non validi: {wrong}")
                if any(not c.test_case_title.strip() for c in response.test_cases):
                    raise JsonGenerationError("caso senza titolo")
                parsed[:] = response.test_cases

            request_json(
                self.llm,
                prompt,
                schema=OutlineResponse,
                thinking_budget=OUTLINE_THINKING_BUDGET,
                raw_file=raw_file,
                check=check,
                on_status=self.on_status,
            )
            return [(refs[c.requirement_ref], c) for c in parsed]

        parts = split_on_truncation(list(indexes), run, on_split=self._split_message("requirements"))
        return [item for part in parts for item in part]

    def _split_message(self, what: str):
        def message(first: int, second: int) -> None:
            self._status(f"Response too long: splitting the {what} into {first} + {second}…")

        return message

    # -------------------------------------------------------------- fase B

    def _detail(
        self, story: UserStory, number: int, cases: Sequence[_Case], corrections: Sequence[str] = ()
    ) -> None:
        """Genera gli step di ``cases`` (divisi a metà se la risposta è troppo lunga)."""

        def run(subset: Sequence[_Case]) -> None:
            prompt_file, raw_file = self._files(number, "step")
            prompt = build_detail_prompt(
                [c.payload(story) for c in subset],
                story.payload(sorted({c.requirement_index for c in subset}), with_ref=False),
                story.ui_spec,
                corrections,
                output_file=prompt_file,
            )
            expected = [c.ref for c in subset]
            details: dict[str, DetailCase] = {}

            def check(data: Any) -> None:
                try:
                    response = DetailResponse.model_validate(data)
                except ValidationError as exc:
                    raise JsonGenerationError(f"step non validi: {exc}") from exc
                refs = [c.case_ref for c in response.test_cases]
                if sorted(refs) != sorted(expected):
                    raise JsonGenerationError(f"casi attesi {expected}, ricevuti {refs}")
                details.clear()
                details.update({c.case_ref: c for c in response.test_cases})

            request_json(
                self.llm,
                prompt,
                schema=DetailResponse,
                thinking_budget=DETAIL_THINKING_BUDGET,
                raw_file=raw_file,
                check=check,
                on_status=self.on_status,
            )
            for case in subset:
                case.detail = details[case.ref]
                case.issues = check_standards(case.detail, case.outline.test_type)

        split_on_truncation(list(cases), run, on_split=self._split_message("test cases"))

    def _fix(self, story: UserStory, number: int, case: _Case) -> None:
        """Rigenera un caso non conforme; tiene la versione con meno errori."""
        for attempt in range(1, MAX_FIX_ATTEMPTS + 1):
            if not case.issues:
                return
            self._status(
                f"US {number} · fixing '{case.outline.test_case_title}' "
                f"(attempt {attempt}/{MAX_FIX_ATTEMPTS})…"
            )
            best_detail, best_issues = case.detail, case.issues
            self._detail(story, number, [case], [f"{case.ref}: {i}" for i in best_issues])
            if len(case.issues) > len(best_issues):
                case.detail, case.issues = best_detail, best_issues

    # -------------------------------------------------------------- assemblaggio

    def _test_case(self, story: UserStory, case: _Case) -> dict[str, Any]:
        requirement = story.requirements[case.requirement_index]
        detail = case.detail
        assert detail is not None
        test_case = TestCase(
            initiative_id=str(requirement.get("iniziativa_id") or ""),
            application_module=None,
            user_requirement_id=requirement.get("user_requirement_id"),
            id1=None,
            macro_area=self.initiative.name.strip() or None,
            id2=None,
            requirement_use_case=use_case_name(str(requirement.get("source_id") or "")),
            id3=str(requirement.get("confluence_id") or ""),
            scenario_functionality=SCENARIO_FUNCTIONALITY,
            scenario_test_case=case.outline.scenario_test_case,
            test_case_title=case.outline.test_case_title,
            test_case_macro_funzionalita=requirement.get("title"),
            description_notes=detail.description_notes.strip() or None,
            test_type=case.outline.test_type.value,
            level="",
            estimated_duration=ESTIMATED_DURATION,
            steps=[
                {
                    "step_number": number,
                    "step_type": step.step_type,
                    "step_name": step.step_name.strip(),
                    "actions_and_data": step.actions_and_data.strip(),
                    "expected_result": step.expected_result.strip(),
                }
                for number, step in enumerate(detail.steps, start=1)  # numerazione sempre 1..n
            ],
        )
        data = test_case.model_dump(mode="json")
        # epic_id non è nel modello TestCase ma resta nel JSON (tracciabilità).
        data["epic_id"] = requirement.get("epic_id")
        return data

    # -------------------------------------------------------------- esecuzione

    def _story(
        self, story: UserStory, number: int, total: int, known_titles: list[str], precise: bool
    ) -> list[dict[str, Any]]:
        """Fase A e fase B di una user story; restituisce i suoi casi completi."""
        prefix = f"US {number}/{total} · {story.label}"
        self._status(f"{prefix} · case list…")
        indexes = list(range(len(story.requirements)))
        outline = self._outline(story, number, indexes, known_titles, story.target)

        # Copertura: ogni requisito deve avere almeno un caso (non in modalità preciso,
        # dove il numero può non bastare).
        missing = [i for i in indexes if all(i != idx for idx, _ in outline)]
        if missing and not precise:
            self._status(f"{prefix} · case list for {len(missing)} uncovered requirements…")
            titles = known_titles + [c.test_case_title for _, c in outline]
            outline += self._outline(story, number, missing, titles, None)
            missing = [i for i in indexes if all(i != idx for idx, _ in outline)]
        for i in missing:
            self.warnings.append(
                f"{story.label}: nessun caso di test per il requisito "
                f"'{story.requirements[i].get('title')}'."
            )
        if not outline:
            return []

        cases = [_Case(f"C{n}", index, item) for n, (index, item) in enumerate(outline, start=1)]
        for start in range(0, len(cases), DETAIL_BATCH_SIZE):
            batch = cases[start : start + DETAIL_BATCH_SIZE]
            self._status(
                f"{prefix} · steps for cases {start + 1}-{start + len(batch)} of {len(cases)}…"
            )
            self._detail(story, number, batch)
        result = []
        for case in cases:
            self._fix(story, number, case)
            if case.issues:
                self.warnings.append(
                    f"{story.label} · '{case.outline.test_case_title}': " + "; ".join(case.issues)
                )
            result.append(self._test_case(story, case))
        known_titles += [c.outline.test_case_title for c in cases]
        return result

    def run(
        self,
        stories: Sequence[UserStory],
        json_file: Path = TEST_CASES_JSON_FILE,
        precise: bool = False,
    ) -> GenerationReport:
        known_titles: list[str] = []
        test_cases: list[dict[str, Any]] = []
        failed: list[str] = []
        for number, story in enumerate(stories, start=1):
            try:
                test_cases += self._story(story, number, len(stories), known_titles, precise)
            except Exception as exc:  # one user story must not stop the others
                failed.append(story.label)
                self.warnings.insert(
                    0,
                    f"USER STORY NON GENERATA: {story.label} ({type(exc).__name__}: {exc}). "
                    "La test list non contiene i suoi casi: rigenera.",
                )
            if self.partial_file is not None:
                save_json({"test_cases": test_cases}, self.partial_file)

        if not test_cases:
            raise JsonGenerationError(
                "Nessun caso di test generato. " + (self.warnings[0] if self.warnings else "")
            )
        data = {"test_cases": test_cases}
        return GenerationReport(
            data, save_json(data, json_file), len(stories), self.calls, self.warnings, failed
        )


def generate_test_list(
    requirements_data: Mapping[str, Any],
    ui_spec: Mapping[str, Any] | None,
    initiative: InitiativeData,
    llm: JsonLlmClient,
    target_count: int | None,
    count_mode: str,
    on_status: StatusCallback | None = None,
    json_file: Path = TEST_CASES_JSON_FILE,
    **paths: Any,
) -> GenerationReport:
    """Pianifica per user story e genera la test list completa."""
    stories = plan_user_stories(requirements_data, ui_spec)
    if not stories:
        raise JsonGenerationError("Il JSON dei requisiti non contiene requisiti.")
    allocate_targets(stories, target_count, count_mode)
    generator = TestListGenerator(llm, initiative, on_status, **paths)
    return generator.run(stories, json_file, precise=count_mode == COUNT_MODE_PRECISE and bool(target_count))
