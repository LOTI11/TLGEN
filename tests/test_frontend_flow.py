"""UI regression tests for the Streamlit frontend (no LLM calls, no pipeline run).

They protect the widget keys, the session state and the 5-step flow while the
look of the app evolves.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontend.config import PIPELINE_STAGES, STEPS  # noqa: E402
from frontend.state import STAGE_DONE, STAGE_ERROR  # noqa: E402

APP = str(ROOT / "app.py")
STATE_KEY = "tlgen"
INITIATIVE_KEYS = ("init_name", "init_id", "init_epic", "init_requirement_id")


@pytest.fixture
def docs_dir(tmp_path, monkeypatch):
    (tmp_path / "a.md").write_text("# A", encoding="utf-8")
    (tmp_path / "b.md").write_text("# B", encoding="utf-8")
    ui_dir = tmp_path / "figma"
    ui_dir.mkdir()
    (ui_dir / "home.png").write_bytes(b"\x89PNG\r\n\x1a\nfake")
    (ui_dir / "flow.pdf").write_bytes(b"%PDF-1.4 fake")
    (ui_dir / "notes.txt").write_text("ignored", encoding="utf-8")
    import frontend.documents as documents

    monkeypatch.setattr(documents, "DOCUMENTS_DIR", tmp_path)
    monkeypatch.setattr(documents, "UI_DOCUMENTS_DIR", ui_dir)
    return tmp_path


def _app() -> AppTest:
    at = AppTest.from_file(APP, default_timeout=30).run()
    assert not at.exception
    return at


def _click(at: AppTest, label: str) -> AppTest:
    button = next(b for b in at.button if b.label == label)
    return button.click().run()


def _state(at: AppTest):
    return at.session_state[STATE_KEY]


def _go_to_initiative(at: AppTest) -> AppTest:
    at.checkbox(key="repo_doc_a.md").check().run()
    return _click(at, "Continue")


def _fill_initiative(at: AppTest) -> AppTest:
    for key in INITIATIVE_KEYS:
        at.text_input(key=key).input(f"value of {key}")
    at.run()
    return _click(at, "Continue")


def test_documents_step_lists_repository_documents(docs_dir):
    at = _app()
    assert _state(at).step == 0
    assert at.checkbox(key="repo_doc_a.md")
    assert at.checkbox(key="repo_doc_b.md")


def test_continue_requires_a_document(docs_dir):
    at = _click(_app(), "Continue")
    assert _state(at).step == 0
    assert at.error


def test_documents_selection_is_stored(docs_dir):
    at = _app()
    at.checkbox(key="repo_doc_a.md").check().run()
    at.checkbox(key="repo_doc_b.md").check().run()
    assert _state(at).selected_repo_documents == {"a.md", "b.md"}


def test_ui_tab_lists_only_png_and_pdf(docs_dir):
    at = _app()
    assert at.checkbox(key="ui_doc_home.png")
    assert at.checkbox(key="ui_doc_flow.pdf")
    assert not any(c.key == "ui_doc_notes.txt" for c in at.checkbox)
    # The user story checkboxes are not mixed with the UI ones.
    assert not any(c.key == "repo_doc_home.png" for c in at.checkbox)


def test_ui_selection_is_stored_separately(docs_dir):
    at = _app()
    at.checkbox(key="ui_doc_home.png").check().run()
    at.checkbox(key="repo_doc_a.md").check().run()
    state = _state(at)
    assert state.selected_repo_ui == {"home.png"}
    assert state.selected_repo_documents == {"a.md"}


def test_remove_unselects_a_folder_document(docs_dir):
    at = _app()
    at.checkbox(key="repo_doc_a.md").check().run()
    at.checkbox(key="ui_doc_home.png").check().run()
    at = at.button(key="ui_rm_repository_home.png").click().run()
    assert not at.exception
    state = _state(at)
    assert state.selected_repo_ui == set()
    assert at.checkbox(key="ui_doc_home.png").value is False
    assert state.selected_repo_documents == {"a.md"}


def test_remove_drops_an_uploaded_document(docs_dir):
    at = _app()
    _state(at).uploaded_documents["new.md"] = b"# New"
    at.run()
    at = at.button(key="rm_upload_new.md").click().run()
    assert not at.exception
    assert _state(at).uploaded_documents == {}


def test_ui_designs_alone_are_not_enough(docs_dir):
    at = _app()
    at.checkbox(key="ui_doc_home.png").check().run()
    at = _click(at, "Continue")
    assert _state(at).step == 0
    assert at.error


def test_review_lists_user_stories_and_ui_designs(docs_dir):
    at = _app()
    at.checkbox(key="ui_doc_flow.pdf").check().run()
    at = _fill_initiative(_go_to_initiative(at))
    at.number_input(key="test_count_input").set_value(3).run()
    at = _click(at, "Continue")
    headings = [m.value for m in at.markdown]
    assert "#### User stories · 1" in headings
    assert "#### UI designs · 1" in headings


def test_initiative_requires_all_fields(docs_dir):
    at = _go_to_initiative(_app())
    assert _state(at).step == 1
    at.text_input(key="init_name").input("only name").run()
    at = _click(at, "Continue")
    assert _state(at).step == 1
    assert len(at.error) >= 1


def test_test_count_must_be_at_least_one(docs_dir):
    at = _fill_initiative(_go_to_initiative(_app()))
    assert _state(at).step == 2
    at = _click(at, "Continue")
    assert _state(at).step == 2
    assert at.error


def test_full_flow_reaches_review_and_keeps_values(docs_dir):
    at = _fill_initiative(_go_to_initiative(_app()))
    at.number_input(key="test_count_input").set_value(3).run()
    at = _click(at, "Continue")
    state = _state(at)
    assert state.step == STEPS.index("Review")
    assert state.test_count == 3
    assert state.initiative["name"] == "value of init_name"
    assert any(b.label == "Generate Test List" for b in at.button)

    # Going back keeps what the user typed.
    at = _click(at, "Back")
    at = _click(at, "Back")
    assert at.text_input(key="init_name").value == "value of init_name"


def test_generation_screen_without_run_does_not_call_the_pipeline(docs_dir):
    at = _app()
    state = _state(at)
    state.step = len(STEPS) - 1
    at.run()
    assert not at.exception
    assert not any(b.label == "Download Test List" for b in at.get("download_button"))


def test_generation_screen_completed_offers_download(docs_dir, tmp_path):
    export = tmp_path / "Export.xlsm"
    export.write_bytes(b"xlsm")
    at = _app()
    state = _state(at)
    state.step = len(STEPS) - 1
    state.stage_status = {key: STAGE_DONE for key, _, _ in PIPELINE_STAGES}
    state.export_file = str(export)
    at.run()
    assert not at.exception
    assert len(at.get("download_button")) == 1
    assert at.success


def test_progress_board_updates_in_place_without_duplicates():
    """The board is built once and synced many times (as during a real run)."""
    script = """
from frontend.components.progress_step import _build_board, _sync
from frontend.state import STAGE_DONE, STAGE_RUNNING, get_state, set_stage_status

state = get_state()
board = _build_board()
set_stage_status("inputs", STAGE_RUNNING, "Reading 1/2")
_sync(board, state)
state.requirements_text = "some text"
set_stage_status("inputs", STAGE_DONE, "2 documents read")
_sync(board, state)
_sync(board, state)  # a repeated sync must not duplicate the result expander
"""
    sys.path.insert(0, str(ROOT))
    at = AppTest.from_string(script, default_timeout=30).run()
    assert not at.exception
    assert len(at.expander) == 1
    assert at.expander[0].label == "Prepared input (requirements text)"


def test_back_is_disabled_when_navigation_is_locked():
    script = """
from frontend.components.navigation import render_navigation
from frontend.state import get_state

state = get_state()
state.step = 4
render_navigation(state, locked=True)
"""
    at = AppTest.from_string(script, default_timeout=30).run()
    assert not at.exception
    assert at.button(key="btn_back_locked").disabled


def test_back_is_enabled_again_once_generation_finishes(docs_dir, monkeypatch):
    """Pending run -> Back locked while it runs, redrawn enabled afterwards (no Gemini)."""
    import frontend.components.progress_step as progress_step
    from frontend.state import get_state

    def fake_run_generation(update_ui):
        get_state().generation_pending = False  # what the real pipeline does first

    monkeypatch.setattr(progress_step, "run_generation", fake_run_generation)
    at = _app()
    state = _state(at)
    state.step = len(STEPS) - 1
    state.generation_pending = True
    at.run()
    assert not at.exception
    assert not at.button(key="btn_back").disabled
    assert not any(b.key == "btn_back_locked" for b in at.button)


def _generation_state_with_test_cases(at: AppTest, requested: int, generated: int):
    import json

    state = _state(at)
    state.step = len(STEPS) - 1
    state.test_count = requested
    state.stage_status = {key: STAGE_DONE for key, _, _ in PIPELINE_STAGES}
    state.test_cases_json = json.dumps({"test_cases": [{} for _ in range(generated)]})
    return state


@pytest.mark.parametrize(
    ("requested", "generated", "difference"), [(2, 5, "+3"), (8, 5, "-3"), (4, 4, "+0")]
)
def test_generation_screen_compares_requested_and_generated_test_cases(
    docs_dir, tmp_path, requested, generated, difference
):
    export = tmp_path / "Export.xlsm"
    export.write_bytes(b"xlsm")
    at = _app()
    _generation_state_with_test_cases(at, requested, generated).export_file = str(export)
    at.run()
    assert not at.exception
    metrics = {m.label: m.value for m in at.metric}
    assert metrics == {
        "Requested (indicative)": str(requested),
        "Generated": str(generated),
        "Difference": difference,
    }


def test_generation_card_names_the_precise_mode(docs_dir, tmp_path):
    export = tmp_path / "Export.xlsm"
    export.write_bytes(b"xlsm")
    at = _app()
    state = _generation_state_with_test_cases(at, 6, 4)
    state.export_file = str(export)
    state.test_count_mode = "preciso"
    at.run()
    assert not at.exception
    assert {m.label for m in at.metric} == {"Requested (precise)", "Generated", "Difference"}
    assert any("Precise mode" in c.value for c in at.caption)


def test_test_count_mode_defaults_to_indicative_and_is_remembered(docs_dir):
    at = _fill_initiative(_go_to_initiative(_app()))
    assert _state(at).step == 2
    assert at.segmented_control(key="test_count_mode_input").value == "Indicativo"
    assert _state(at).test_count_mode == "indicativo"

    at.segmented_control(key="test_count_mode_input").set_value("Preciso").run()
    assert _state(at).test_count_mode == "preciso"

    at.number_input(key="test_count_input").set_value(5).run()
    at = _click(at, "Continue")  # review
    assert _state(at).step == STEPS.index("Review")
    at = _click(at, "Back")
    assert at.segmented_control(key="test_count_mode_input").value == "Preciso"
    assert _state(at).test_count_mode == "preciso"


def test_generation_screen_has_no_comparison_before_test_cases_exist(docs_dir):
    at = _app()
    _state(at).step = len(STEPS) - 1
    at.run()
    assert not at.exception
    assert len(at.metric) == 0


def test_generation_screen_error_has_no_download(docs_dir):
    at = _app()
    state = _state(at)
    state.step = len(STEPS) - 1
    state.stage_status[PIPELINE_STAGES[0][0]] = STAGE_ERROR
    state.stage_detail[PIPELINE_STAGES[0][0]] = "boom"
    at.run()
    assert not at.exception
    assert len(at.get("download_button")) == 0
