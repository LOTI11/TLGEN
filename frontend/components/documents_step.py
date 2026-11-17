from __future__ import annotations

from pathlib import Path

import streamlit as st

from frontend.config import DOCUMENTS_DIR, SUPPORTED_EXTENSIONS
from frontend.documents import DocumentRef, format_size, list_available_documents
from frontend.state import AppState


def selected_documents(state: AppState) -> list[DocumentRef]:
    """Current selection (repository + uploaded), in display order."""
    repo = [
        d
        for d in list_available_documents(DOCUMENTS_DIR)
        if d.name in state.selected_repo_documents
    ]
    uploaded = [
        DocumentRef(name, "upload", len(data))
        for name, data in state.uploaded_documents.items()
    ]
    return repo + uploaded


def render_documents_table(docs: list[DocumentRef]) -> None:
    st.dataframe(
        [
            {
                "Document": d.name,
                "Type": Path(d.name).suffix.lstrip(".").upper(),
                "Source": "Repository" if d.source == "repository" else "Uploaded",
                "Size": format_size(d.size_bytes),
            }
            for d in docs
        ],
        hide_index=True,
        width="stretch",
    )


def _render_available(state: AppState) -> None:
    st.markdown("#### Available Documents")
    st.caption(f"From `{DOCUMENTS_DIR.name}`")
    available = list_available_documents(DOCUMENTS_DIR)
    if not available:
        st.info("No documents loaded")
        return
    selected: set[str] = set()
    for doc in available:
        name_col, size_col = st.columns([5, 1], vertical_alignment="center")
        with name_col:
            checked = st.checkbox(
                doc.name,
                value=doc.name in state.selected_repo_documents,
                key=f"repo_doc_{doc.name}",
            )
        size_col.caption(format_size(doc.size_bytes))
        if checked:
            selected.add(doc.name)
    state.selected_repo_documents = selected


def _store_uploads(state: AppState) -> None:
    files = st.session_state.get(f"uploader_{state.uploader_nonce}") or []
    for f in files:
        state.uploaded_documents[f.name] = f.getvalue()
    state.uploader_nonce += 1  # reset the widget; files now live in state


def _render_upload(state: AppState) -> None:
    st.markdown("#### Upload Documents")
    st.caption("Supported: " + ", ".join(f".{e}" for e in SUPPORTED_EXTENSIONS))
    st.file_uploader(
        "Drag and drop files here",
        type=list(SUPPORTED_EXTENSIONS),
        accept_multiple_files=True,
        key=f"uploader_{state.uploader_nonce}",
        on_change=_store_uploads,
        args=(state,),
        label_visibility="collapsed",
    )
    for name, data in list(state.uploaded_documents.items()):
        name_col, size_col, btn_col = st.columns([5, 2, 1], vertical_alignment="center")
        name_col.write(name)
        size_col.caption(format_size(len(data)))
        if btn_col.button("✕", key=f"rm_{name}", help=f"Remove {name}", type="tertiary"):
            del state.uploaded_documents[name]
            st.rerun()


def _render_selected(state: AppState) -> None:
    docs = selected_documents(state)
    title_col, count_col = st.columns([4, 1], vertical_alignment="center")
    title_col.markdown("#### Selected Documents")
    count_col.badge(f"{len(docs)} selected", color="blue" if docs else "gray")
    if docs:
        render_documents_table(docs)
    else:
        st.caption("No documents selected.")


def render_documents_step(state: AppState) -> None:
    left, right = st.columns(2, gap="large")
    with left, st.container(border=True):
        _render_available(state)
    with right, st.container(border=True):
        _render_upload(state)
    with st.container(border=True):
        _render_selected(state)
