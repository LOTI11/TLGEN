from __future__ import annotations

import streamlit as st

from frontend.actions import on_generate_clicked
from frontend.config import PROGRESS_STEP, REVIEW_STEP
from frontend.state import AppState, go_to
from frontend.validation import validate_step


def render_navigation(state: AppState) -> None:
    st.divider()
    back_col, _, next_col = st.columns([1, 4, 1])

    if back_col.button("Back", disabled=state.step == 0, width="stretch"):
        go_to(state.step - 1)
        st.rerun()

    if state.step == PROGRESS_STEP:
        return

    if state.step == REVIEW_STEP:
        next_col.button(
            "Generate Test List",
            type="primary",
            width="stretch",
            on_click=on_generate_clicked,
        )
        return

    if next_col.button("Continue", type="primary", width="stretch"):
        errors = validate_step(state, state.step)
        if errors:
            for message in errors:
                st.error(message)
        else:
            go_to(state.step + 1)
            st.rerun()
