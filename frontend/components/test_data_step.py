from __future__ import annotations

import streamlit as st

from frontend.config import TEST_COUNT_MODE_HELP, TEST_COUNT_MODES
from frontend.state import AppState
from frontend.ui import card, step_title


def _render_mode_selector(state: AppState) -> None:
    """Indicative (model decides) or precise (exact number) use of the test count."""
    current_label = next(
        label for label, value in TEST_COUNT_MODES.items() if value == state.test_count_mode
    )
    choice = st.segmented_control(
        "Come usare il numero",
        list(TEST_COUNT_MODES),
        default=current_label,
        required=True,
        key="test_count_mode_input",
    )
    state.test_count_mode = TEST_COUNT_MODES[choice or current_label]
    st.caption(TEST_COUNT_MODE_HELP[state.test_count_mode])


def render_test_data_step(state: AppState) -> None:
    step_title(
        "Test Data",
        ":material/fact_check:",
        "Specify how many tests the initiative requires and how the number is used.",
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
        _render_mode_selector(state)
