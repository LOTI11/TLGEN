"""Minimal CSS used for the segmented stepper and layout spacing."""

from __future__ import annotations

import streamlit as st

_CSS = """
<style>
.block-container { max-width: 1100px; padding-top: 2.5rem; }
.tl-eyebrow { font-size: .75rem; letter-spacing: .08em; text-transform: uppercase;
              color: #2563EB; font-weight: 600; margin-bottom: .25rem; }
.tl-stepper { display: flex; gap: .5rem; margin: 1.25rem 0 .5rem; }
.tl-step { flex: 1; }
.tl-step-bar { height: 4px; border-radius: 2px; background: #E5E7EB; }
.tl-step-label { margin-top: .4rem; font-size: .85rem; color: #9CA3AF; }
.tl-step.done .tl-step-bar { background: #93C5FD; }
.tl-step.done .tl-step-label { color: #4B5563; }
.tl-step.current .tl-step-bar { background: #2563EB; }
.tl-step.current .tl-step-label { color: #1F2937; font-weight: 600; }
.tl-field-label { font-size: .75rem; color: #6B7280; text-transform: uppercase;
                  letter-spacing: .04em; margin-bottom: .1rem; }
.tl-field-value { font-size: 1rem; font-weight: 500; word-break: break-word; }
</style>
"""


def inject_css() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)
