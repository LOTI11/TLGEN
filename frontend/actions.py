"""CTA handlers: the integration point between the UI and the backend services.

Implemented stages: ``inputs``, ``prompt1``, ``requirements``, ``prompt2``.
Still to connect: test_cases, export. Add each one as a
``_work_*`` function and run it from ``run_generation`` through ``_run_stage``.
"""

from __future__ import annotations

import time
from collections.abc import Callable

import streamlit as st

from frontend.config import PROGRESS_STEP
from frontend.documents import read_document_bytes, selected_documents
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
    build_requirements_text,
    save_requirements_text,
)
from services.json_generation import (
    REQUIREMENTS_JSON_FILE,
    REQUIREMENTS_RAW_FILE,
    JsonGenerationError,
    generate_json_file,
)
from services.prompt_builder import (
    PromptBuildError,
    build_requirements_prompt,
    build_test_cases_prompt,
)

UpdateUi = Callable[[], None]
# A stage worker receives a "report progress" callback and returns the final detail text.
StageWorker = Callable[[Callable[[str], None]], str]

# Errors that a stage may raise and that must be shown to the user.
_STAGE_ERRORS = (DocumentReadError, PromptBuildError, JsonGenerationError, OSError)


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
        ("prompt2", lambda report: _work_write_prompt2(state)),
        # TODO: test_cases -> export
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
    set_stage_status(key, STAGE_DONE, detail)
    update_ui()
    return True


def _work_prepare_inputs(state: AppState, report: Callable[[str], None]) -> str:
    """Stage 1: read the selected documents into ``state.requirements_text``."""
    documents = [
        SourceDocument(ref.name, read_document_bytes(ref, state))
        for ref in selected_documents(state)
    ]
    text = build_requirements_text(
        documents,
        lambda index, total, name: report(f"Reading {index}/{total}: {name}"),
    )
    save_requirements_text(text)
    state.requirements_text = text
    return f"{len(documents)} documents read · {len(text):,} characters"


def _work_write_prompt1(state: AppState) -> str:
    """Stage 2: merge the Prompt 1 template with the requirements text."""
    prompt = build_requirements_prompt(state.requirements_text)
    state.requirements_prompt = prompt
    return f"Prompt generated · {len(prompt):,} characters"


@st.cache_resource(show_spinner=False)
def _gemini_service():
    """One Gemini client shared by all stages and reruns (same model as main.py)."""
    from services.gemini_service import GeminiService  # lazy: heavy Google SDK import

    return GeminiService()


def _work_generate_requirements(state: AppState, report: Callable[[str], None]) -> str:
    """Stage 3: send Prompt 1 to Gemini and save the requirements JSON."""
    report("Connecting to Gemini…")
    try:
        gemini = _gemini_service()
    except Exception as exc:  # missing credentials / invalid .env configuration
        raise JsonGenerationError(f"Configurazione Gemini non valida: {exc}") from exc

    report("Waiting for the model response…")
    started = time.monotonic()
    result = generate_json_file(
        state.requirements_prompt, REQUIREMENTS_RAW_FILE, REQUIREMENTS_JSON_FILE, gemini
    )
    state.requirements_json = result.text

    items = result.data.get("requirements") if isinstance(result.data, dict) else None
    count = f"{len(items)} requirements · " if isinstance(items, list) else ""
    return f"{count}JSON saved · {time.monotonic() - started:.0f}s"


def _work_write_prompt2(state: AppState) -> str:
    """Stage 4: merge the Prompt 2 template with the requirements JSON."""
    prompt = build_test_cases_prompt()
    state.test_cases_prompt = prompt
    return f"Prompt generated · {len(prompt):,} characters"
