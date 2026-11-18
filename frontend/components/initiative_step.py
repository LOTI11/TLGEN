from __future__ import annotations

import streamlit as st

from frontend.state import AppState
from frontend.ui import card, initiative_grid, step_title


def render_initiative_step(state: AppState) -> None:
    step_title(
        "Initiative",
        ":material/assignment:",
        "Describe the initiative the Test List refers to.",
    )
    with card("initiative"):
        for col, key, label in initiative_grid():
            with col:
                state.initiative[key] = st.text_input(
                    label, value=state.initiative[key], key=f"init_{key}"
                )
