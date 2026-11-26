"""CTA handlers: the integration point between the UI and the backend services.

All pipeline stages are connected: inputs, prompt1, requirements, ui, prompt2
(plan), test_cases, boost (only when Test Boost is on), export. Each one is a ``_work_*`` function run from
``run_generation`` through ``_run_stage``.
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable

import streamlit as st

from frontend.config import PROGRESS_STEP
from frontend.documents import UI_DESIGNS, read_document_bytes, selected_documents
from frontend.state import (
    STAGE_DONE,
    STAGE_ERROR,
    STAGE_RUNNING,
    AppState,
    get_state,
    go_to,
    reset_pipeline,
    set_stage_status,
)
from services.input_preparation import (
    DocumentReadError,
    SourceDocument,
    read_documents,
    save_requirements_text,
)
from services.json_generation import JsonGenerationError
from services.llm_types import IncompleteResponseError
from services.prompt_builder import InitiativeData, PromptBuildError, build_requirements_prompt
from services.requirements_extraction import extract_requirements
from services.test_boost import bucket_summary, run_boost
from services.test_case_generation import allocate_targets, generate_test_list, plan_user_stories
from services.test_list_export import ExportError, export_test_list
from services.ui_analysis import UiAnalysisError, analyze_ui, prepare_ui_files

UpdateUi = Callable[[], None]
# A stage worker receives a "report progress" callback and returns the final detail text.
StageWorker = Callable[[Callable[[str], None]], str]

# Errors that a stage may raise and that must be shown to the user.
_STAGE_ERRORS = (
    DocumentReadError,
    PromptBuildError,
    JsonGenerationError,
    IncompleteResponseError,
    UiAnalysisError,
    ExportError,
    OSError,
)


def on_generate_clicked() -> None:
    """Generate Test List: reset progress and move to the Generation screen."""
    reset_pipeline()
    get_state().generation_pending = True
    go_to(PROGRESS_STEP)


def run_generation(update_ui: UpdateUi) -> None:
    """Run the pipeline once per click; ``update_ui`` redraws the progress board."""
    state = get_state()
    if not state.generation_pending:
        return
    state.generation_pending = False

    stages: tuple[tuple[str, StageWorker], ...] = (
        ("inputs", lambda report: _work_prepare_inputs(state, report)),
        ("prompt1", lambda report: _work_write_prompt1(state)),
        ("requirements", lambda report: _work_generate_requirements(state, report)),
        ("ui", lambda report: _work_analyze_ui(state, report)),
        ("prompt2", lambda report: _work_plan_test_cases(state)),
        ("test_cases", lambda report: _work_generate_test_cases(state, report)),
        ("boost", lambda report: _work_boost(state, report)),
        ("export", lambda report: _work_export(state, report)),
    )
    for key, worker in stages:
        if not _run_stage(key, worker, update_ui):
            return


def _run_stage(key: str, worker: StageWorker, update_ui: UpdateUi) -> bool:
    """Run one stage updating its status; return False if it failed."""

    def report(detail: str) -> None:
        set_stage_status(key, STAGE_RUNNING, detail)
        update_ui()

    report("Starting…")
    try:
        detail = worker(report)
    except _STAGE_ERRORS as exc:
        set_stage_status(key, STAGE_ERROR, str(exc))
        update_ui()
        return False
    except Exception as exc:  # Gemini/network errors: show them instead of crashing the page
        set_stage_status(key, STAGE_ERROR, f"{type(exc).__name__}: {exc}")
        update_ui()
        return False
    set_stage_status(key, STAGE_DONE, detail)
    update_ui()
    return True


@st.cache_resource(show_spinner=False)
def _gemini_service():
    """One Gemini client shared by all stages and reruns (same model as main.py)."""
    from services.gemini_service import GeminiService  # lazy: heavy Google SDK import

    return GeminiService()


def _connect_gemini(report: Callable[[str], None]):
    report("Connecting to Gemini…")
    try:
        return _gemini_service()
    except Exception as exc:  # missing credentials / invalid .env configuration
        raise JsonGenerationError(f"Configurazione Gemini non valida: {exc}") from exc


def _initiative_data(state: AppState) -> InitiativeData:
    """Initiative fields typed by the user, in the shape the prompt builder expects."""
    initiative = state.initiative
    return InitiativeData(
        name=initiative["name"],
        id=initiative["id"],
        epic=initiative["epic"],
        requirement_id=initiative["requirement_id"],
    )


def _elapsed(started: float) -> str:
    return f"{time.monotonic() - started:.0f}s"


def _requests(parts: int) -> list[str]:
    return [f"split into {parts} requests"] if parts > 1 else []


def _work_prepare_inputs(state: AppState, report: Callable[[str], None]) -> str:
    """Stage 1: read the selected user stories (one text per document)."""
    documents = [
        SourceDocument(ref.name, read_document_bytes(ref, state))
        for ref in selected_documents(state)
    ]
    texts = read_documents(
        documents,
        lambda index, total, name: report(f"Reading {index}/{total}: {name}"),
    )
    text = "\n".join(texts)
    save_requirements_text(text)
    state.source_texts = texts
    state.requirements_text = text
    return f"{len(documents)} documents read · {len(text):,} characters"


def _work_write_prompt1(state: AppState) -> str:
    """Stage 2: merge the Prompt 1 template with the requirements text."""
    prompt = build_requirements_prompt(state.requirements_text, _initiative_data(state))
    state.requirements_prompt = prompt
    return f"Prompt generated · {len(prompt):,} characters"


def _work_generate_requirements(state: AppState, report: Callable[[str], None]) -> str:
    """Stage 3: extract the requirements (split by documents if the answer is too long)."""
    gemini = _connect_gemini(report)
    started = time.monotonic()
    result = extract_requirements(state.source_texts, _initiative_data(state), gemini, report)
    state.requirements_json = result.text
    count = len(result.data["requirements"])
    return " · ".join(
        [f"{count} requirements", "JSON saved", *_requests(result.parts), _elapsed(started)]
    )


def _work_analyze_ui(state: AppState, report: Callable[[str], None]) -> str:
    """UI stage: send all the selected Figma designs to Gemini and save the UI spec.

    Optional: without UI designs the stage is skipped and the test cases use the
    user stories only.
    """
    state.ui_spec_json = ""
    refs = selected_documents(state, group=UI_DESIGNS)
    if not refs:
        return "No UI designs selected · skipped"

    report(f"Checking {len(refs)} UI designs…")
    files = prepare_ui_files(
        [SourceDocument(ref.name, read_document_bytes(ref, state, UI_DESIGNS)) for ref in refs]
    )
    gemini = _connect_gemini(report)
    started = time.monotonic()
    result = analyze_ui(files, state.requirements_json, gemini, on_status=report)
    state.ui_spec_json = result.text
    open_points = result.data.get("open_points") or []
    if open_points:
        state.warnings.append(
            f"UI designs: {len(open_points)} open points (unreadable text or uncertain "
            "links to the user stories). See the UI spec JSON in the Analyze UI designs stage."
        )
    screens = len(result.data.get("screens") or [])
    return " · ".join(
        [
            f"{len(files)} designs analyzed",
            f"{screens} screens",
            *_requests(result.parts),
            _elapsed(started),
        ]
    )


def _plan(state: AppState):
    stories = plan_user_stories(
        json.loads(state.requirements_json),
        json.loads(state.ui_spec_json) if state.ui_spec_json else None,
    )
    allocate_targets(stories, state.test_count, state.test_count_mode)
    return stories


def _work_plan_test_cases(state: AppState) -> str:
    """Stage 4: split the work by user story; the plan is shown to the user."""
    stories = _plan(state)
    if not stories:
        raise JsonGenerationError("Il JSON dei requisiti non contiene requisiti.")
    lines = [
        f"{n}. {s.label} · {len(s.requirements)} requirements · "
        f"{len((s.ui_spec or {}).get('screens') or [])} UI screens"
        + (f" · {s.target} test cases requested" if s.target is not None else "")
        for n, s in enumerate(stories, start=1)
    ]
    state.test_cases_prompt = "\n".join(lines)
    with_ui = sum(1 for s in stories if s.ui_spec)
    return f"{len(stories)} user stories · {with_ui} with UI screens"


def _work_generate_test_cases(state: AppState, report: Callable[[str], None]) -> str:
    """Stage 5: case list and steps for each user story, checked against the standard."""
    gemini = _connect_gemini(report)
    started = time.monotonic()
    result = generate_test_list(
        json.loads(state.requirements_json),
        json.loads(state.ui_spec_json) if state.ui_spec_json else None,
        _initiative_data(state),
        gemini,
        state.test_count,
        state.test_count_mode,
        on_status=report,
    )
    state.test_cases_json = result.text
    if result.warnings:
        state.warnings.append(
            f"Test cases: {len(result.warnings)} points to review:\n"
            + "\n".join(f"- {w}" for w in result.warnings)
        )
    cases = result.data["test_cases"]
    steps = sum(len(c["steps"]) for c in cases)
    failed = (
        [f"{len(result.failed_stories)} user stories NOT generated (see the warnings)"]
        if result.failed_stories
        else []
    )
    return " · ".join(
        [
            f"{len(cases)} test cases",
            f"{steps} steps",
            f"{result.stories} user stories",
            *failed,
            f"{result.calls} requests",
            _elapsed(started),
        ]
    )


def _work_boost(state: AppState, report: Callable[[str], None]) -> str:
    """Test Boost stage: complete the short cases to meet the step distribution.

    Off: nothing changes and the export uses the test cases as generated. On: the
    completed test list replaces the JSON read by the export (the generated one is
    kept in test_cases_pre_boost.json, the added steps in boost_report.json).
    """
    state.boost_report_json = ""
    if not state.test_boost:
        return "Off · skipped"
    report("Completing the cases below their step range…")
    result, _ = run_boost(
        json.loads(state.test_cases_json),
        json.loads(state.ui_spec_json) if state.ui_spec_json else None,
    )
    state.boost_report_json = json.dumps(result.to_json(), indent=2, ensure_ascii=False)
    missed = [b for b in result.buckets if not b.met]
    if missed or result.warnings:
        state.warnings.append(
            "Test Boost: the step distribution is NOT fully met.\n"
            + "\n".join(
                f"- {b.bucket.label} steps: {b.actual} cases out of {b.target} required" for b in missed
            )
            + ("\n" if missed and result.warnings else "")
            + "\n".join(f"- {w}" for w in result.warnings)
        )
    return " · ".join(
        [
            bucket_summary(result),
            f"{result.added_steps:,} steps added",
            "distribution met" if result.met else "distribution NOT met",
        ]
    )


def _work_export(state: AppState, report: Callable[[str], None]) -> str:
    """Stage 6: import the test cases into the XLSM template."""
    report("Writing the Excel file…")
    output_file = export_test_list()
    state.export_file = str(output_file)
    return f"{output_file.name} · {output_file.stat().st_size / 1024:,.0f} KB"
