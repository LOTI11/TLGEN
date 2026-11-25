from __future__ import annotations

import html
import json
from dataclasses import dataclass, field
from pathlib import Path

import streamlit as st
from streamlit.delta_generator import DeltaGenerator

from frontend.actions import on_generate_clicked, run_generation
from frontend.config import PIPELINE_STAGES
from frontend.state import (
    STAGE_DONE,
    STAGE_ERROR,
    STAGE_PENDING,
    STAGE_RUNNING,
    AppState,
)
from frontend.ui import card, step_title
from services.test_list_export import XLSM_MIME_TYPE

# status -> (label, glyph shown in the circle; None = stage number)
_STATUS_DISPLAY = {
    STAGE_PENDING: ("Waiting", None),
    STAGE_RUNNING: ("In progress", None),
    STAGE_DONE: ("Completed", "✓"),
    STAGE_ERROR: ("Error", "!"),
}

# Stage key -> (expander title, state attribute holding the output, code language).
# Add an entry here when a new stage produces a result to inspect.
STAGE_OUTPUTS: dict[str, tuple[str, str, str | None]] = {
    "inputs": ("Prepared input (requirements text)", "requirements_text", None),
    "prompt1": ("Prompt 1 (final prompt)", "requirements_prompt", None),
    "requirements": ("Requirements (JSON)", "requirements_json", "json"),
    "ui": ("UI spec from Figma (JSON)", "ui_spec_json", "json"),
    "prompt2": ("Plan by user story", "test_cases_prompt", None),
    "test_cases": ("Test cases (JSON)", "test_cases_json", "json"),
    "boost": ("Test Boost report: buckets and added steps (JSON)", "boost_report_json", "json"),
}


@dataclass
class _Board:
    """Elements created once per run and updated in place (no full redraw)."""

    progress: DeltaGenerator
    cards: dict[str, DeltaGenerator]
    outputs: dict[str, DeltaGenerator]
    shown: set[str] = field(default_factory=set)


def _stage_card(number: int, label: str, description: str, status: str, detail: str) -> str:
    status_label, glyph = _STATUS_DISPLAY[status]
    detail_html = f'<div class="tl-stage-detail">{html.escape(detail)}</div>' if detail else ""
    return (
        f'<div class="tl-stage {status}">'
        f'<div class="tl-stage-dot">{glyph or number}</div>'
        f'<div class="tl-stage-body"><div class="tl-stage-title">{html.escape(label)}</div>'
        f'<div class="tl-stage-desc">{html.escape(description)}</div>{detail_html}</div>'
        f'<div class="tl-stage-pill">{status_label}</div></div>'
    )


def _build_board() -> _Board:
    progress = st.progress(0.0)
    cards: dict[str, DeltaGenerator] = {}
    outputs: dict[str, DeltaGenerator] = {}
    for key, _, _ in PIPELINE_STAGES:
        with st.container(key=f"stage-{key}"):
            cards[key] = st.empty()  # stateless card, replaced on every status change
            outputs[key] = st.container()  # holds the result expander, written once
    return _Board(progress, cards, outputs)


def _show_output(board: _Board, state: AppState, stage_key: str) -> None:
    """Collapsible result of a stage, shown once right below its card."""
    if stage_key in board.shown or stage_key not in STAGE_OUTPUTS:
        return
    title, attribute, language = STAGE_OUTPUTS[stage_key]
    content = getattr(state, attribute)
    if not content:
        return
    with board.outputs[stage_key], st.expander(title):
        st.code(content, language=language, wrap_lines=True, height=300)
    board.shown.add(stage_key)


def _sync(board: _Board, state: AppState) -> None:
    """Bring the board in line with the state, touching only what changed."""
    total = len(PIPELINE_STAGES)
    done = sum(s == STAGE_DONE for s in state.stage_status.values())
    board.progress.progress(done / total, text=f"{done} of {total} stages completed")
    for number, (key, label, description) in enumerate(PIPELINE_STAGES, start=1):
        board.cards[key].html(
            _stage_card(
                number, label, description, state.stage_status[key], state.stage_detail.get(key, "")
            )
        )
        _show_output(board, state, key)


def render_progress_step(state: AppState) -> None:
    step_title("Generation", ":material/rocket_launch:", "Follow the progress of each stage.")
    board = _build_board()
    _sync(board, state)

    hint = st.empty()
    if state.generation_pending:
        hint.caption("Generation in progress: keep this page open.")
    run_generation(lambda: _sync(board, state))
    hint.empty()

    for warning in state.warnings:
        st.warning(warning, icon=":material/warning:")

    if any(s == STAGE_ERROR for s in state.stage_status.values()):
        _render_error_actions()
    elif all(s == STAGE_DONE for s in state.stage_status.values()):
        _render_completion(state)
    _render_test_count_summary(state)
    _render_boost_summary(state)


def _render_boost_summary(state: AppState) -> None:
    """Test Boost: required vs obtained cases for each step bucket."""
    if not state.boost_report_json:
        return
    try:
        report = json.loads(state.boost_report_json)
    except ValueError:
        return
    buckets = report.get("buckets") or []
    met = all(b["ottenuto"] >= b["obiettivo"] for b in buckets) and not report.get("avvisi")
    with card("boost-summary"):
        with st.container(horizontal=True, vertical_alignment="center"):
            st.markdown("#### Step distribution (Test Boost)")
            st.space("stretch")
            st.badge(
                "Met" if met else "Not met",
                icon=":material/check_circle:" if met else ":material/warning:",
                color="green" if met else "orange",
            )
        st.table(
            [
                {
                    "Steps": b["fascia"],
                    "Required": b["obiettivo"],
                    "Obtained": b["ottenuto"],
                    "Share": f"{b['percentuale']:.1f}%",
                }
                for b in buckets
            ],
            hide_index=True,
            alt="Required and obtained test cases for each step bucket",
        )
        real, added = report.get("step_reali", 0), report.get("step_aggiunti", 0)
        st.caption(
            f"{real:,} steps generated by the model · {added:,} steps added from "
            "parser/boost/boostSteps.json. The added steps are listed in the report above."
        )


def _generated_test_count(state: AppState) -> int | None:
    """Number of test cases in the generated JSON (None while not available)."""
    if not state.test_cases_json:
        return None
    try:
        items = json.loads(state.test_cases_json).get("test_cases")
    except (ValueError, AttributeError):
        return None
    return len(items) if isinstance(items, list) else None


def _render_test_count_summary(state: AppState) -> None:
    """Requested (guideline) vs generated number of test cases."""
    generated = _generated_test_count(state)
    if generated is None:
        return
    requested = state.test_count
    mode = state.test_count_mode
    difference = generated - requested
    with card("test-count"):
        st.markdown("#### Number of test cases")
        requested_col, generated_col, difference_col = st.columns(3)
        requested_col.metric(f"Requested ({'precise' if mode == 'preciso' else 'indicative'})", requested)
        generated_col.metric("Generated", generated)
        difference_col.metric("Difference", f"{difference:+d}")
        if difference == 0:
            st.caption("The generated number matches the requested one.")
        elif mode == "preciso":
            direction = "more" if difference > 0 else "fewer"
            st.caption(
                f"Precise mode: {abs(difference)} {direction} test cases than requested were "
                "generated. The integrity of the Test List takes precedence over the number."
            )
        else:
            st.caption(
                "Indicative mode: the model decided how many test cases the requirements need; "
                "the requested number was only a reference."
            )


def _render_error_actions() -> None:
    st.caption("Fix the issue above, then try again (Back lets you change the input).")
    st.button(
        "Retry",
        icon=":material/refresh:",
        key="btn_retry",
        type="primary",
        on_click=on_generate_clicked,
    )


def _render_completion(state: AppState) -> None:
    """Final result: success message and download of the generated Test List."""
    export_file = Path(state.export_file)
    if not export_file.is_file():
        st.error("The generated file was not found.", icon=":material/error:")
        return
    st.success("Your Test List is ready.", icon=":material/check_circle:")
    st.download_button(
        "Download Test List",
        data=export_file.read_bytes,  # read only when the user clicks
        file_name=export_file.name,
        mime=XLSM_MIME_TYPE,
        icon=":material/download:",
        key="btn_download",
        type="primary",
        on_click="ignore",
    )
