"""Streamlit session-state management (frontend state only)."""

from __future__ import annotations

from dataclasses import dataclass, field

import streamlit as st

from frontend.config import DEFAULT_TEST_COUNT_MODE, PIPELINE_STAGES, STEPS

_KEY = "tlgen"

STAGE_PENDING = "pending"
STAGE_RUNNING = "running"
STAGE_DONE = "done"
STAGE_ERROR = "error"


def _initial_stage_status() -> dict[str, str]:
    return {key: STAGE_PENDING for key, _, _ in PIPELINE_STAGES}


@dataclass
class AppState:
    step: int = 0
    selected_repo_documents: set[str] = field(default_factory=set)
    uploaded_documents: dict[str, bytes] = field(default_factory=dict)
    uploader_nonce: int = 0
    # UI designs (PNG/PDF exported from Figma): optional, same structure as above.
    selected_repo_ui: set[str] = field(default_factory=set)
    uploaded_ui: dict[str, bytes] = field(default_factory=dict)
    ui_uploader_nonce: int = 0
    initiative: dict[str, str] = field(
        default_factory=lambda: {
            "name": "",
            "id": "",
            "epic": "",
            "requirement_id": "",
        }
    )
    test_count: int = 0
    test_count_mode: str = DEFAULT_TEST_COUNT_MODE
    # Test Boost: complete the short cases to meet the step distribution (off by default).
    test_boost: bool = False
    # Pipeline progress, to be updated by the backend integration.
    stage_status: dict[str, str] = field(default_factory=_initial_stage_status)
    stage_detail: dict[str, str] = field(default_factory=dict)
    generation_pending: bool = False
    # Output of stage 1 (Prepare inputs): input text for Prompt 1, also per document.
    requirements_text: str = ""
    source_texts: list[str] = field(default_factory=list)
    # Output of stage 2 (Write prompt 1): final prompt sent to the model.
    requirements_prompt: str = ""
    # Output of stage 3 (Generate requirements): formatted requirements JSON.
    requirements_json: str = ""
    # Output of the UI stage: formatted UI spec JSON ("" = no UI designs selected).
    ui_spec_json: str = ""
    # Output of stage 4 (Write prompt 2): final prompt for test case generation.
    test_cases_prompt: str = ""
    # Output of stage 5 (Generate test cases): formatted test cases JSON.
    test_cases_json: str = ""
    # Output of the Test Boost stage: report JSON (buckets and added steps); "" = off.
    boost_report_json: str = ""
    # Output of stage 6 (Build Test List): path of the generated XLSM file.
    export_file: str = ""
    # Non-blocking notices for the user (e.g. JSON repaired automatically).
    warnings: list[str] = field(default_factory=list)


def get_state() -> AppState:
    if _KEY not in st.session_state:
        st.session_state[_KEY] = AppState()
    return st.session_state[_KEY]


def go_to(step: int) -> None:
    get_state().step = max(0, min(step, len(STEPS) - 1))


def set_stage_status(stage_key: str, status: str, detail: str = "") -> None:
    """Update one pipeline stage (pending/running/done/error) and its detail text."""
    state = get_state()
    state.stage_status[stage_key] = status
    state.stage_detail[stage_key] = detail


def reset_pipeline() -> None:
    state = get_state()
    state.stage_status = _initial_stage_status()
    state.stage_detail = {}
    state.requirements_text = ""
    state.source_texts = []
    state.requirements_prompt = ""
    state.requirements_json = ""
    state.ui_spec_json = ""
    state.test_cases_prompt = ""
    state.test_cases_json = ""
    state.boost_report_json = ""
    state.export_file = ""
    state.warnings = []
