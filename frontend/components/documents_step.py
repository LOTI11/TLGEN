from __future__ import annotations

from pathlib import Path

import streamlit as st

from frontend.documents import (
    UI_DESIGNS,
    USER_STORIES,
    DocumentGroup,
    DocumentRef,
    format_size,
    list_group_documents,
    selected_documents,
)
from frontend.state import AppState
from frontend.ui import card, step_title

_FILE_ICONS = {
    ".md": ":material/description:",
    ".png": ":material/image:",
    ".pdf": ":material/picture_as_pdf:",
}

# Per group: box title, icon, caption and the label shown in the selected list.
_GROUP_TEXT = {
    "stories": (
        "User stories",
        ":material/description:",
        "Required. The functional source of the requirements and of the test cases.",
        "User story",
    ),
    "ui": (
        "UI designs",
        ":material/palette:",
        "Optional. Screens exported from Figma: several PNG and PDF files are analyzed together.",
        "UI design",
    ),
}


def _icon(name: str) -> str:
    return _FILE_ICONS.get(Path(name).suffix.lower(), ":material/draft:")


def _prefix(group: DocumentGroup) -> str:
    """Widget-key prefix: none for the user stories (keys kept as before), ``ui_`` for UI."""
    return "" if group is USER_STORIES else f"{group.key}_"


def _checkbox_key(group: DocumentGroup, name: str) -> str:
    return f"{_prefix(group) or 'repo_'}doc_{name}"


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


# ---------------------------------------------------------------- input boxes


def _uploader_key(state: AppState, group: DocumentGroup) -> str:
    return f"{_prefix(group)}uploader_{getattr(state, group.nonce_attr)}"


def _store_uploads(state: AppState, group: DocumentGroup) -> None:
    files = st.session_state.get(_uploader_key(state, group)) or []
    uploaded = group.uploaded(state)
    for f in files:
        uploaded[f.name] = f.getvalue()
    # Reset the widget; the files now live in the state and in the selected list.
    setattr(state, group.nonce_attr, getattr(state, group.nonce_attr) + 1)


def _render_available(state: AppState, group: DocumentGroup, available: list[DocumentRef]) -> None:
    st.caption(f"From the `{group.directory().name}` folder")
    if not available:
        st.info("No documents in the folder.", icon=":material/folder_off:")
        return
    current = group.selected_names(state)
    selected: set[str] = set()
    for index, doc in enumerate(available):
        with st.container(key=f"docrow-{_prefix(group)}{index}"):
            name_col, size_col = st.columns([6, 1.5], vertical_alignment="center")
            with name_col:
                checked = st.checkbox(
                    f"{_icon(doc.name)} {doc.name}",
                    value=doc.name in current,
                    key=_checkbox_key(group, doc.name),
                )
            size_col.caption(format_size(doc.size_bytes))
        if checked:
            selected.add(doc.name)
    group.set_selected_names(state, selected)


def _render_input_box(state: AppState, group: DocumentGroup) -> None:
    title, icon, caption, _ = _GROUP_TEXT[group.key]
    with card(f"{_prefix(group)}input"):
        st.markdown(f"#### {icon} {title}")
        st.caption(caption)
        st.file_uploader(
            f"Upload {title.lower()} (" + ", ".join(f".{e}" for e in group.extensions) + ")",
            type=list(group.extensions),
            accept_multiple_files=True,
            key=_uploader_key(state, group),
            on_change=_store_uploads,
            args=(state, group),
        )
        _render_available(state, group, list_group_documents(group))


# ---------------------------------------------------------------- selected list


def _remove(state: AppState, group: DocumentGroup, ref: DocumentRef) -> None:
    """Callback of the Remove button: unselect a folder file or drop an uploaded one."""
    if ref.source == "repository":
        group.selected_names(state).discard(ref.name)
        st.session_state[_checkbox_key(group, ref.name)] = False  # allowed in a callback
    else:
        group.uploaded(state).pop(ref.name, None)


def _render_selected_rows(state: AppState, group: DocumentGroup, docs: list[DocumentRef]) -> None:
    label = _GROUP_TEXT[group.key][3]
    for index, doc in enumerate(docs):
        with st.container(key=f"docrow-{_prefix(group)}selected-{index}"):
            name_col, info_col, btn_col = st.columns([6, 3, 1.6], vertical_alignment="center")
            name_col.write(f"{_icon(doc.name)} {doc.name}")
            source = "Folder" if doc.source == "repository" else "Uploaded"
            info_col.caption(f"{label} · {source} · {format_size(doc.size_bytes)}")
            btn_col.button(
                "Remove",
                key=f"{_prefix(group)}rm_{doc.source}_{doc.name}",
                icon=":material/close:",
                type="tertiary",
                help=f"Remove {doc.name}",
                on_click=_remove,
                args=(state, group, doc),
            )


def _render_selected(state: AppState) -> None:
    stories = selected_documents(state, group=USER_STORIES)
    designs = selected_documents(state, group=UI_DESIGNS)
    with card("selected"):
        with st.container(horizontal=True, vertical_alignment="center"):
            st.markdown("#### Selected documents")
            st.space("stretch")
            st.badge(
                f"{len(stories)} user {'story' if len(stories) == 1 else 'stories'}",
                icon=":material/description:",
                color="blue" if stories else "gray",
            )
            st.badge(
                f"{len(designs)} UI {'design' if len(designs) == 1 else 'designs'}",
                icon=":material/palette:",
                color="violet" if designs else "gray",
            )
        if not stories and not designs:
            st.caption("No documents selected. Choose at least one user story.")
            return
        _render_selected_rows(state, USER_STORIES, stories)
        _render_selected_rows(state, UI_DESIGNS, designs)
        if not designs:
            st.caption("No UI designs: the test cases will use the user stories only.")


def render_documents_step(state: AppState) -> None:
    step_title(
        "Documents",
        ":material/folder_open:",
        "Choose the user stories and, optionally, the UI designs used to generate the Test List.",
    )
    stories_col, ui_col = st.columns(2, gap="large")
    with stories_col:
        _render_input_box(state, USER_STORIES)
    with ui_col:
        _render_input_box(state, UI_DESIGNS)
    # Drawn after the boxes so it reflects the checkboxes of this run.
    _render_selected(state)
