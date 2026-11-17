"""Streamlit session-state management (frontend state only)."""

from __future__ import annotations

from dataclasses import dataclass, field

import streamlit as st

from frontend.config import PIPELINE_STAGES, STEPS

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
    initiative: dict[str, str] = field(
        default_factory=lambda: {
            "name": "",
            "id": "",
            "epic": "",
            "requirement_id": "",
        }
    )
    test_count: int = 0
    # Pipeline progress, to be updated by the backend integration.
    stage_status: dict[str, str] = field(default_factory=_initial_stage_status)
    stage_message: str = ""
    generate_requested: bool = False


def get_state() -> AppState:
    if _KEY not in st.session_state:
        st.session_state[_KEY] = AppState()
    return st.session_state[_KEY]


def go_to(step: int) -> None:
    get_state().step = max(0, min(step, len(STEPS) - 1))


def set_stage_status(stage_key: str, status: str, message: str = "") -> None:
    """Update one pipeline stage (pending/running/done/error)."""
    state = get_state()
    state.stage_status[stage_key] = status
    state.stage_message = message
