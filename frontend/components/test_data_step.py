from __future__ import annotations

import streamlit as st

from frontend.state import AppState


def render_test_data_step(state: AppState) -> None:
    st.subheader("Test Data")
    with st.container(border=True):
        state.test_count = int(
            st.number_input(
                "Numero di test necessari per l'iniziativa",
                min_value=0,
                step=1,
                value=state.test_count,
                key="test_count_input",
            )
        )
