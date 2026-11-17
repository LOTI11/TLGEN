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


def _render_board(state: AppState) -> None:
    total = len(PIPELINE_STAGES)
    done = sum(s == STAGE_DONE for s in state.stage_status.values())
    st.progress(done / total, text=f"{done} of {total} stages completed")
    cards = "".join(
        _stage_card(i, label, desc, state.stage_status[key], state.stage_detail.get(key, ""))
        for i, (key, label, desc) in enumerate(PIPELINE_STAGES, start=1)
    )
    st.markdown(f'<div class="tl-stages">{cards}</div>', unsafe_allow_html=True)


def _render_preview(title: str, content: str) -> None:
    if not content:
        return
    with st.expander(title):
        st.text_area(title, content, height=300, disabled=True, label_visibility="collapsed")


def render_progress_step(state: AppState) -> None:
    st.markdown("#### Generation Progress")
    board = st.empty()

    def draw() -> None:
        with board.container():
            _render_board(state)

    draw()
    run_generation(draw)

    errors = [
        f"**{label}** — {state.stage_detail[key]}"
        for key, label, _ in PIPELINE_STAGES
        if state.stage_status[key] == STAGE_ERROR
    ]
    for message in errors:
        st.error(message)
    if errors:
        st.caption("Fix the issue above (use Back to change the input), then generate again.")
        return

    _render_preview("Prepared input (requirements text)", state.requirements_text)
    _render_preview("Prompt 1 (final prompt)", state.requirements_prompt)
    if any(s == STAGE_PENDING for s in state.stage_status.values()):
        st.info("Next stages are not connected to the backend yet.")
