from __future__ import annotations

import streamlit as st

from frontend.components.documents_step import render_documents_table
from frontend.documents import UI_DESIGNS, USER_STORIES, selected_documents
from frontend.state import AppState
from frontend.ui import card, initiative_grid, labeled_value, step_title


def render_review_step(state: AppState) -> None:
    step_title(
        "Review",
        ":material/rule:",
        "Check the information below before generating the Test List.",
    )

    with card("review-initiative"):
        st.markdown("#### Initiative")
        for col, key, label in initiative_grid():
            labeled_value(col, label, state.initiative[key])

    with card("review-test-data"):
        st.markdown("#### Test Data")
        count_col, mode_col, boost_col = st.columns(3)
        labeled_value(count_col, "Numero di test necessari", str(state.test_count))
        labeled_value(mode_col, "Come usare il numero", state.test_count_mode.capitalize())
        labeled_value(boost_col, "Test Boost", "Attivo" if state.test_boost else "Disattivo")

    with card("review-documents"):
        docs = selected_documents(state, group=USER_STORIES)
        st.markdown(f"#### User stories · {len(docs)}")
        if docs:
            render_documents_table(docs)
        else:
            st.caption("No user stories selected.")

    with card("review-ui"):
        designs = selected_documents(state, group=UI_DESIGNS)
        st.markdown(f"#### UI designs · {len(designs)}")
        if designs:
            render_documents_table(designs)
        else:
            st.caption("No UI designs: the test cases will use the user stories only.")
