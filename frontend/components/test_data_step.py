from __future__ import annotations

import streamlit as st

from frontend.state import AppState
from frontend.ui import card, step_title


def render_test_data_step(state: AppState) -> None:
    step_title(
        "Test Data",
        ":material/fact_check:",
        "Specify how many tests the initiative requires.",
    )
    with card("test-data"):
        state.test_count = int(
            st.number_input(
                "Numero di test necessari per l'iniziativa",
                min_value=0,
                step=1,
                value=state.test_count,
                key="test_count_input",
                help="Enter at least 1.",
            )
        )
