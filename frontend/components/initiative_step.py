from __future__ import annotations

import streamlit as st

from frontend.state import AppState
from frontend.validation import INITIATIVE_LABELS


def render_initiative_step(state: AppState) -> None:
    st.subheader("Initiative")
    fields = list(INITIATIVE_LABELS.items())
    with st.container(border=True):
        for row in (fields[:2], fields[2:]):
            for col, (key, label) in zip(st.columns(2, gap="large"), row):
                with col:
                    state.initiative[key] = st.text_input(
                        label, value=state.initiative[key], key=f"init_{key}"
                    )
