"""Small shared UI helpers (layout only, no state or business logic)."""

from __future__ import annotations

import re

import streamlit as st
from streamlit.delta_generator import DeltaGenerator

from frontend.config import INITIATIVE_LABELS


def card(name: str) -> DeltaGenerator:
    """Bordered card; the key exposes a ``.st-key-card-<name>`` class for the CSS."""
    return st.container(border=True, key=f"card-{name}")


def step_title(title: str, icon: str, caption: str | None = None) -> None:
    st.subheader(title, icon=icon)
    if caption:
        st.caption(caption)


_MARKDOWN_SPECIAL = re.compile(r"([\\`*_{}\[\]()#+\-.!|~<>$])")


def labeled_value(container: DeltaGenerator, label: str, value: str) -> None:
    """Read-only 'label / value' pair; the value is shown literally (no Markdown)."""
    escaped = _MARKDOWN_SPECIAL.sub(lambda m: "\\" + m.group(1), value) if value else "—"
    with container.container(gap=None):
        st.caption(label)
        st.markdown(f"**{escaped}**")


def initiative_grid() -> list[tuple[DeltaGenerator, str, str]]:
    """Two-by-two grid for the initiative fields: (column, state key, label)."""
    fields = list(INITIATIVE_LABELS.items())
    cells: list[tuple[DeltaGenerator, str, str]] = []
    for row in (fields[:2], fields[2:]):
        for col, (key, label) in zip(st.columns(2, gap="large"), row):
            cells.append((col, key, label))
    return cells
