from __future__ import annotations

import html

import streamlit as st

from frontend.components.documents_step import (
    render_documents_table,
    selected_documents,
)
from frontend.state import AppState
from frontend.validation import INITIATIVE_LABELS


def _field(col, label: str, value: str) -> None:
    col.markdown(
        f'<div class="tl-field-label">{html.escape(label)}</div>'
        f'<div class="tl-field-value">{html.escape(value) or "—"}</div>',
        unsafe_allow_html=True,
    )


def render_review_step(state: AppState) -> None:
    st.markdown("#### Review")
    st.caption("Check the information below before generating the Test List.")

    with st.container(border=True):
        st.markdown("**Initiative**")
        fields = list(INITIATIVE_LABELS.items())
        for row in (fields[:2], fields[2:]):
            for col, (key, label) in zip(st.columns(2), row):
                _field(col, label, state.initiative[key])

    with st.container(border=True):
        st.markdown("**Test Data**")
        _field(st, "Numero di test necessari", str(state.test_count))

    with st.container(border=True):
        docs = selected_documents(state)
        st.markdown(f"**Documents** · {len(docs)}")
        if docs:
            render_documents_table(docs)
        else:
            st.caption("No documents selected.")
