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
.tl-stages { display: flex; flex-direction: column; gap: .6rem; margin-top: .75rem; }
.tl-stage { display: flex; align-items: center; gap: 1rem; padding: .85rem 1rem;
            border: 1px solid #E5E7EB; border-left: 4px solid #D1D5DB; border-radius: 8px; }
.tl-stage-dot { width: 2rem; height: 2rem; border-radius: 50%; flex: none; display: flex;
                align-items: center; justify-content: center; font-weight: 600;
                background: #F3F4F6; color: #6B7280; }
.tl-stage-body { flex: 1; min-width: 0; }
.tl-stage-title { font-weight: 600; }
.tl-stage-desc, .tl-stage-detail { font-size: .85rem; color: #6B7280; }
.tl-stage-detail { margin-top: .15rem; color: #374151; white-space: pre-line; }
.tl-stage-pill { font-size: .75rem; font-weight: 600; padding: .2rem .65rem;
                 border-radius: 999px; background: #F3F4F6; color: #6B7280; }
.tl-stage.running { border-left-color: #2563EB; background: #F5F9FF; }
.tl-stage.running .tl-stage-dot { background: #2563EB; color: #fff; animation: tl-pulse 1.2s infinite; }
.tl-stage.running .tl-stage-pill { background: #DBEAFE; color: #1D4ED8; }
.tl-stage.done { border-left-color: #16A34A; }
.tl-stage.done .tl-stage-dot { background: #16A34A; color: #fff; }
.tl-stage.done .tl-stage-pill { background: #DCFCE7; color: #15803D; }
.tl-stage.error { border-left-color: #DC2626; background: #FEF7F7; }
.tl-stage.error .tl-stage-dot { background: #DC2626; color: #fff; }
.tl-stage.error .tl-stage-pill { background: #FEE2E2; color: #B91C1C; }
@keyframes tl-pulse { 0%,100% { box-shadow: 0 0 0 0 rgba(37,99,235,.45); }
                      50% { box-shadow: 0 0 0 8px rgba(37,99,235,0); } }
</style>
"""


def inject_css() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)
