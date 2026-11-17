from __future__ import annotations

import streamlit as st

from frontend.config import PIPELINE_STAGES
from frontend.state import (
    STAGE_DONE,
    STAGE_ERROR,
    STAGE_PENDING,
    STAGE_RUNNING,
    AppState,
)

# status -> (badge label, badge colour, badge icon)
_STATUS_DISPLAY = {
    STAGE_PENDING: ("Waiting", "gray", ":material/schedule:"),
    STAGE_RUNNING: ("In progress", "blue", ":material/autorenew:"),
    STAGE_DONE: ("Completed", "green", ":material/check_circle:"),
    STAGE_ERROR: ("Error", "red", ":material/error:"),
}


def render_progress_step(state: AppState) -> None:
    total = len(PIPELINE_STAGES)
    done = sum(s == STAGE_DONE for s in state.stage_status.values())

    st.markdown("#### Generation Progress")
    st.progress(done / total, text=f"{done} of {total} stages completed")

    for idx, (key, label, description) in enumerate(PIPELINE_STAGES, start=1):
        status = state.stage_status[key]
        badge_text, color, icon = _STATUS_DISPLAY[status]
        with st.container(border=True):
            num_col, text_col, status_col = st.columns([1, 8, 3], vertical_alignment="center")
            num_col.markdown(f"### {idx}")
            text_col.markdown(f"**{label}**")
            text_col.caption(description)
            status_col.badge(badge_text, icon=icon, color=color)

    if state.stage_message:
        st.info(state.stage_message)
    elif state.generate_requested:
        st.info("Generation is not connected to the backend yet.")
