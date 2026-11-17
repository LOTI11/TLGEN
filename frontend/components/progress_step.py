from __future__ import annotations

import html

import streamlit as st

from frontend.actions import run_generation
from frontend.config import PIPELINE_STAGES
from frontend.state import (
    STAGE_DONE,
    STAGE_ERROR,
    STAGE_PENDING,
    STAGE_RUNNING,
    AppState,
)

# status -> (label, glyph shown in the circle; None = stage number)
_STATUS_DISPLAY = {
    STAGE_PENDING: ("Waiting", None),
    STAGE_RUNNING: ("In progress", None),
    STAGE_DONE: ("Completed", "✓"),
    STAGE_ERROR: ("Error", "!"),
}


def _stage_card(number: int, label: str, description: str, status: str, detail: str) -> str:
    status_label, glyph = _STATUS_DISPLAY[status]
    detail_html = f'<div class="tl-stage-detail">{html.escape(detail)}</div>' if detail else ""
    return (
        f'<div class="tl-stage {status}">'
        f'<div class="tl-stage-dot">{glyph or number}</div>'
        f'<div class="tl-stage-body"><div class="tl-stage-title">{html.escape(label)}</div>'
        f'<div class="tl-stage-desc">{html.escape(description)}</div>{detail_html}</div>'
        f'<div class="tl-stage-pill">{status_label}</div></div>'
    )


# Stage key -> (expander title, state attribute holding the output, code language).
# Add an entry here when a new stage produces a result to inspect.
STAGE_OUTPUTS: dict[str, tuple[str, str, str | None]] = {
    "inputs": ("Prepared input (requirements text)", "requirements_text", None),
    "prompt1": ("Prompt 1 (final prompt)", "requirements_prompt", None),
    "requirements": ("Requirements (JSON)", "requirements_json", "json"),
    "prompt2": ("Prompt 2 (final prompt)", "test_cases_prompt", None),
}


def _render_output(state: AppState, stage_key: str) -> None:
    """Collapsible result of a stage, shown right below its card."""
    if stage_key not in STAGE_OUTPUTS:
        return
    title, attribute, language = STAGE_OUTPUTS[stage_key]
    content = getattr(state, attribute)
    if content:
        with st.expander(title):
            st.code(content, language=language, wrap_lines=True, height=300)


def _render_board(state: AppState) -> None:
    total = len(PIPELINE_STAGES)
    done = sum(s == STAGE_DONE for s in state.stage_status.values())
    st.progress(done / total, text=f"{done} of {total} stages completed")
    for number, (key, label, description) in enumerate(PIPELINE_STAGES, start=1):
        card = _stage_card(
            number, label, description, state.stage_status[key], state.stage_detail.get(key, "")
        )
        st.markdown(card, unsafe_allow_html=True)
        _render_output(state, key)


def render_progress_step(state: AppState) -> None:
    st.markdown("#### Generation Progress")
    board = st.empty()

    def draw() -> None:
        with board.container():
            _render_board(state)

    draw()
    run_generation(draw)

    if any(s == STAGE_ERROR for s in state.stage_status.values()):
        st.caption("Fix the issue above (use Back to change the input), then generate again.")
    elif any(s == STAGE_PENDING for s in state.stage_status.values()):
        st.info("Next stages are not connected to the backend yet.")
