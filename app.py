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
from frontend.config import APP_TITLE
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
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    inject_css()
    state = get_state()
    render_header()
    render_stepper(state.step)
    STEP_RENDERERS[state.step](state)
    render_navigation(state)


main()
