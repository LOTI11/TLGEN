"""Custom CSS injection (the stylesheet lives in ``assets/styles.css``)."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

_CSS_FILE = Path(__file__).parent / "assets" / "styles.css"


@st.cache_data(show_spinner=False)
def _read_css() -> str:
    return _CSS_FILE.read_text(encoding="utf-8")


def inject_css() -> None:
    st.html(f"<style>{_read_css()}</style>")
