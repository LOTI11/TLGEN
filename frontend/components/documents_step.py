from __future__ import annotations

from pathlib import Path

import streamlit as st

from frontend.config import DOCUMENTS_DIR, SUPPORTED_EXTENSIONS
from frontend.documents import (
    DocumentRef,
    format_size,
    list_available_documents,
    selected_documents,
)
from frontend.state import AppState
from frontend.ui import card, step_title


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
        alt="Table of the selected documents with type, source and size",
    )


def _render_available(state: AppState, available: list[DocumentRef]) -> None:
    st.markdown("#### Available Documents")
    st.caption(f"From `{DOCUMENTS_DIR.name}`")
    if not available:
        st.info("No documents loaded")
        return
    selected: set[str] = set()
    for index, doc in enumerate(available):
        with st.container(key=f"docrow-{index}"):
            name_col, size_col = st.columns([6, 1.3], vertical_alignment="center")
            with name_col:
                checked = st.checkbox(
                    f":material/description: {doc.name}",
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
    for index, (name, data) in enumerate(list(state.uploaded_documents.items())):
        with st.container(key=f"docrow-upload-{index}"):
            name_col, size_col, btn_col = st.columns([5, 2, 2], vertical_alignment="center")
            name_col.write(f":material/description: {name}")
            size_col.caption(format_size(len(data)))
            if btn_col.button(
                "Remove",
                key=f"rm_{name}",
                icon=":material/close:",
                type="tertiary",
                help=f"Remove {name}",
            ):
                del state.uploaded_documents[name]
                st.rerun()


def _render_selected(state: AppState, available: list[DocumentRef]) -> None:
    docs = selected_documents(state, available)
    with st.container(
        horizontal=True, horizontal_alignment="distribute", vertical_alignment="center"
    ):
        st.markdown("#### Selected Documents")
        st.badge(f"{len(docs)} selected", color="blue" if docs else "gray")
    if docs:
        render_documents_table(docs)
    else:
        st.caption("No documents selected.")


def render_documents_step(state: AppState) -> None:
    step_title(
        "Documents",
        ":material/folder_open:",
        "Choose the documents used to generate the Test List.",
    )
    available = list_available_documents(DOCUMENTS_DIR)
    left, right = st.columns([3, 2], gap="large")  # wider list: file names are long
    with left, card("available"):
        _render_available(state, available)
    with right, card("upload"):
        _render_upload(state)
    with card("selected"):
        _render_selected(state, available)
