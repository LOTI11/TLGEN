from __future__ import annotations

import streamlit as st

from frontend.components.documents_step import render_documents_table
from frontend.documents import selected_documents
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
        labeled_value(st, "Numero di test necessari", str(state.test_count))

    with card("review-documents"):
        docs = selected_documents(state)
        st.markdown(f"#### Documents · {len(docs)}")
        if docs:
            render_documents_table(docs)
        else:
            st.caption("No documents selected.")
