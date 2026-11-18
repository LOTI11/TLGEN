"""Entry point: streamlit run app.py"""

from __future__ import annotations

import streamlit as st

from frontend.components.documents_step import render_documents_step
from frontend.components.header import render_header, render_stepper
from frontend.components.initiative_step import render_initiative_step
from frontend.components.navigation import render_navigation
from frontend.components.progress_step import render_progress_step
from frontend.components.review_step import render_review_step
from frontend.components.test_data_step import render_test_data_step
from frontend.config import APP_TITLE, PROGRESS_STEP
from frontend.state import get_state
from frontend.styles import inject_css

STEP_RENDERERS = (
    render_documents_step,
    render_initiative_step,
    render_test_data_step,
    render_review_step,
    render_progress_step,
)


def main() -> None:
    st.set_page_config(
        page_title=APP_TITLE, page_icon=":material/checklist:", layout="wide"
    )
    inject_css()
    state = get_state()
    render_header()
    render_stepper(state.step)
    # The key changes with the step so the CSS can replay a soft entrance animation.
    body = st.container(key=f"step-body-{state.step}")
    nav = st.empty()  # reserved below the body so it can be redrawn after a run

    if state.step == PROGRESS_STEP:
        # The pipeline runs while the body renders: draw the navigation first,
        # with Back locked, so it cannot be clicked until the process is over.
        generating = state.generation_pending
        with nav.container():
            render_navigation(state, locked=generating)
        with body:
            STEP_RENDERERS[state.step](state)
        if generating:
            with nav.container():
                render_navigation(state)
    else:
        # Validation needs the values written by the widgets of this run.
        with body:
            STEP_RENDERERS[state.step](state)
        with nav.container():
            render_navigation(state)


main()
