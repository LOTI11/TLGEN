from __future__ import annotations

import html

import streamlit as st

from frontend.config import APP_SUBTITLE, APP_TITLE, STEPS


def render_header() -> None:
    st.html('<div class="tl-eyebrow">Quality Engineering</div>')
    st.title(APP_TITLE, icon=":material/checklist:")
    st.caption(APP_SUBTITLE)


def render_stepper(current: int) -> None:
    """Segmented progress indicator (semantic list, no native equivalent)."""
    items = []
    for idx, label in enumerate(STEPS):
        css = "done" if idx < current else "current" if idx == current else ""
        mark = "✓ " if idx < current else ""
        aria = ' aria-current="step"' if idx == current else ""
        items.append(
            f'<div class="tl-step {css}" role="listitem"{aria}><div class="tl-step-bar"></div>'
            f'<div class="tl-step-label">{mark}{idx + 1}. {html.escape(label)}</div></div>'
        )
    st.html(f'<div class="tl-stepper" role="list" aria-label="Progress">{"".join(items)}</div>')
