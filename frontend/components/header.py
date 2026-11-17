from __future__ import annotations

import streamlit as st

from frontend.config import APP_SUBTITLE, APP_TITLE, STEPS


def render_header() -> None:
    st.markdown('<div class="tl-eyebrow">Quality Engineering</div>', unsafe_allow_html=True)
    st.title(APP_TITLE)
    st.caption(APP_SUBTITLE)


def render_stepper(current: int) -> None:
    segments = []
    for idx, label in enumerate(STEPS):
        css = "done" if idx < current else "current" if idx == current else ""
        segments.append(
            f'<div class="tl-step {css}"><div class="tl-step-bar"></div>'
            f'<div class="tl-step-label">{idx + 1}. {label}</div></div>'
        )
    st.markdown(f'<div class="tl-stepper">{"".join(segments)}</div>', unsafe_allow_html=True)
    st.divider()
