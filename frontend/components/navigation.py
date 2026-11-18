from __future__ import annotations

import streamlit as st

from frontend.actions import on_generate_clicked
from frontend.config import PROGRESS_STEP, REVIEW_STEP
from frontend.state import AppState, go_to
from frontend.validation import validate_step


def render_navigation(state: AppState, locked: bool = False) -> None:
    """Back / Continue / Generate bar. ``locked`` disables Back (generation running)."""
    st.space("small")
    has_next = state.step != PROGRESS_STEP
    alignment = "distribute" if has_next else "left"
    errors: list[str] = []

    with st.container(
        horizontal=True, horizontal_alignment=alignment, vertical_alignment="center"
    ):
        # A different key while locked: the same slot is redrawn once the run ends.
        if st.button(
            "Back",
            icon=":material/arrow_back:",
            key="btn_back_locked" if locked else "btn_back",
            disabled=state.step == 0 or locked,
            help="Available when the generation has finished." if locked else None,
        ):
            go_to(state.step - 1)
            st.rerun()

        if state.step == REVIEW_STEP:
            st.button(
                "Generate Test List",
                icon=":material/auto_awesome:",
                key="btn_generate",
                type="primary",
                on_click=on_generate_clicked,
            )
        elif has_next and st.button(
            "Continue",
            icon=":material/arrow_forward:",
            icon_position="right",
            key="btn_continue",
            type="primary",
        ):
            errors = validate_step(state, state.step)
            if not errors:
                go_to(state.step + 1)
                st.rerun()

    if errors:
        st.error(
            "\n".join(f"- {message}" for message in errors),
            title="Complete the required information",
            icon=":material/error:",
        )
