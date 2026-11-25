"""UI designs (Figma PNG/PDF): file checks, prompt construction, Gemini call (mocked)."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import services.ui_analysis as ui_analysis  # noqa: E402
from services.input_preparation import SourceDocument  # noqa: E402
from services.json_generation import JsonGenerationError  # noqa: E402
from services.llm_types import (  # noqa: E402
    IncompleteResponseError,
    LlmResult,
    TruncatedResponseError,
)
from services.prompt_builder import PromptBuildError, build_ui_prompt  # noqa: E402
from services.ui_analysis import (  # noqa: E402
    UiAnalysisError,
    UiFile,
    analyze_ui,
    prepare_ui_files,
)

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16


def _pdf(text: str | None) -> bytes:
    """Minimal one-page PDF; with ``text`` the page has selectable text."""
    stream = f"BT /F1 12 Tf 20 100 Td ({text}) Tj ET".encode() if text else b""
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 200] /Contents 4 0 R "
        b"/Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for number, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % number + body + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objects) + 1)
    out += b"".join(b"%010d 00000 n \n" % o for o in offsets)
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (
        len(objects) + 1,
        xref,
    )
    return bytes(out)


# ---------------------------------------------------------------- file checks


def test_png_and_pdf_are_prepared_together():
    files = prepare_ui_files(
        [SourceDocument("home.png", PNG), SourceDocument("flow.pdf", _pdf("Conferma"))]
    )
    assert [(f.name, f.mime_type) for f in files] == [
        ("home.png", "image/png"),
        ("flow.pdf", "application/pdf"),
    ]
    assert files[0].pages is None
    assert files[1].pages == 1
    assert "Conferma" in files[1].pdf_text


def test_pdf_without_selectable_text_is_accepted_with_empty_text():
    (file,) = prepare_ui_files([SourceDocument("outlined.pdf", _pdf(None))])
    assert file.pages == 1
    assert file.pdf_text == ""


def test_all_problems_are_reported_at_once():
    with pytest.raises(UiAnalysisError) as error:
        prepare_ui_files(
            [
                SourceDocument("fake.png", b"not a png"),
                SourceDocument("broken.pdf", b"%PDF-1.4 broken"),
                SourceDocument("shot.jpg", b"jpeg"),
                SourceDocument("empty.png", b""),
            ]
        )
    message = str(error.value)
    for name in ("fake.png", "broken.pdf", "shot.jpg", "empty.png"):
        assert name in message


def test_default_limits_follow_vertex_ai():
    assert ui_analysis.MAX_FILE_BYTES == {".png": 30 * 1024**2, ".pdf": 50 * 1024**2}
    assert ui_analysis.MAX_TOTAL_BYTES * 4 / 3 < 500 * 1024**2  # base64 overhead included
    assert ui_analysis.MAX_PDF_PAGES == 1000
    assert ui_analysis.MAX_FILES == 3000


def test_total_size_limit(monkeypatch):
    monkeypatch.setattr(ui_analysis, "MAX_TOTAL_BYTES", len(PNG) + 1)
    with pytest.raises(UiAnalysisError, match="MB"):
        prepare_ui_files([SourceDocument("a.png", PNG), SourceDocument("b.png", PNG)])


def test_single_file_limit_depends_on_the_format(monkeypatch):
    monkeypatch.setattr(ui_analysis, "MAX_FILE_BYTES", {".png": len(PNG) - 1, ".pdf": 10**6})
    with pytest.raises(UiAnalysisError) as error:
        prepare_ui_files([SourceDocument("big.png", PNG), SourceDocument("ok.pdf", _pdf("x"))])
    assert "big.png" in str(error.value)
    assert "ok.pdf" not in str(error.value)


def test_pdf_pages_and_file_count_limits(monkeypatch):
    monkeypatch.setattr(ui_analysis, "MAX_PDF_PAGES", 1)
    with pytest.raises(UiAnalysisError, match="pagine"):
        prepare_ui_files([SourceDocument("a.pdf", _pdf("x")), SourceDocument("b.pdf", _pdf("y"))])
    monkeypatch.setattr(ui_analysis, "MAX_FILES", 1)
    with pytest.raises(UiAnalysisError, match="Troppi"):
        prepare_ui_files([SourceDocument("a.png", PNG), SourceDocument("b.png", PNG)])


def test_no_design_is_an_error():
    with pytest.raises(UiAnalysisError):
        prepare_ui_files([])


# ---------------------------------------------------------------- Gemini call (fake)


class FakeJsonLlm:
    """Fake client: returns the queued answers; an exception entry is raised."""

    def __init__(self, answers):
        self.answers = list(answers)
        self.calls = []

    def generate_json(self, prompt, *, files=(), schema=None, thinking_budget=None, on_status=None):
        self.calls.append({"prompt": prompt, "files": list(files), "budget": thinking_budget})
        answer = self.answers.pop(0)
        if isinstance(answer, Exception):
            raise answer
        return LlmResult(answer if isinstance(answer, str) else json.dumps(answer))


def _analyze(tmp_path, files, llm):
    return analyze_ui(
        files,
        REQUIREMENTS,
        llm,
        raw_file=tmp_path / "raw.txt",
        json_file=tmp_path / "ui.json",
        prompt_file=tmp_path / "ui_prompt.md",
    )


def test_all_designs_go_in_one_request_and_the_spec_is_saved(tmp_path):
    files = prepare_ui_files(
        [SourceDocument("home.png", PNG), SourceDocument("flow.pdf", _pdf("Avanti"))]
    )
    spec = {"screens": [{"screen_id": "S1"}], "open_points": []}
    llm = FakeJsonLlm([spec])
    result = _analyze(tmp_path, files, llm)
    assert len(llm.calls) == 1
    assert [(name, mime) for name, _, mime in llm.calls[0]["files"]] == [
        ("home.png", "image/png"),
        ("flow.pdf", "application/pdf"),
    ]
    assert llm.calls[0]["budget"] == ui_analysis.UI_THINKING_BUDGET
    assert "- flow.pdf (PDF, 1 pagine)" in llm.calls[0]["prompt"]
    assert result.data == spec
    assert result.parts == 1
    assert json.loads((tmp_path / "ui.json").read_text(encoding="utf-8")) == spec


def test_invalid_json_is_asked_again_once(tmp_path):
    files = prepare_ui_files([SourceDocument("home.png", PNG)])
    llm = FakeJsonLlm(["not json", {"screens": [{"screen_id": "S1"}]}])
    result = _analyze(tmp_path, files, llm)
    assert len(llm.calls) == 2
    assert result.data["screens"] == [{"screen_id": "S1"}]


def test_answer_without_screens_is_an_error(tmp_path):
    files = prepare_ui_files([SourceDocument("home.png", PNG)])
    with pytest.raises(JsonGenerationError):
        _analyze(tmp_path, files, FakeJsonLlm([{"nothing": 1}, {"nothing": 2}]))


def _part(name):
    return {
        "ui_sources": [{"file_name": name}],
        "screens": [{"screen_id": "S1", "navigation": [{"target_screen_id": "S1"}]}],
        "flows": [{"screen_ids": ["S1"]}],
        "open_points": [],
    }


def test_truncated_answer_splits_the_designs_and_keeps_ids_unique(tmp_path):
    files = prepare_ui_files([SourceDocument("a.png", PNG), SourceDocument("b.png", PNG)])
    truncated = TruncatedResponseError(LlmResult("{", "MAX_TOKENS"))
    llm = FakeJsonLlm([truncated, _part("a"), _part("b")])
    result = _analyze(tmp_path, files, llm)
    assert [len(c["files"]) for c in llm.calls] == [2, 1, 1]
    assert result.parts == 2
    assert [s["screen_id"] for s in result.data["screens"]] == ["P1-S1", "P2-S1"]
    assert result.data["screens"][1]["navigation"][0]["target_screen_id"] == "P2-S1"
    assert [f["screen_ids"] for f in result.data["flows"]] == [["P1-S1"], ["P2-S1"]]
    assert [s["file_name"] for s in result.data["ui_sources"]] == ["a", "b"]


def test_single_design_still_truncated_is_an_error(tmp_path):
    files = prepare_ui_files([SourceDocument("a.png", PNG)])
    llm = FakeJsonLlm([TruncatedResponseError(LlmResult("{", "MAX_TOKENS"))])
    with pytest.raises(JsonGenerationError, match="singolo elemento"):
        _analyze(tmp_path, files, llm)


# ---------------------------------------------------------------- GeminiService.generate_json


def _service(monkeypatch, *responses):
    from services.gemini_service import GeminiService

    client = Mock()
    client.models.generate_content.side_effect = list(responses)
    monkeypatch.setattr(
        "services.gemini_service.service_account.Credentials.from_service_account_file",
        Mock(return_value=SimpleNamespace(project_id="test-project")),
    )
    monkeypatch.setattr("services.gemini_service.genai.Client", Mock(return_value=client))
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")
    service = GeminiService()
    service._sleep = Mock()
    return service, client


def _response(text, finish="STOP", thoughts=100):
    return SimpleNamespace(
        text=text,
        candidates=[SimpleNamespace(finish_reason=SimpleNamespace(name=finish))],
        usage_metadata=SimpleNamespace(
            prompt_token_count=1000, candidates_token_count=50, thoughts_token_count=thoughts
        ),
    )


def test_generate_json_sets_json_mode_budget_and_files(monkeypatch):
    service, client = _service(monkeypatch, _response('{"a": 1}'))
    result = service.generate_json(
        "PROMPT", files=[("home.png", PNG, "image/png")], thinking_budget=1234
    )
    assert result.text == '{"a": 1}'
    assert result.thoughts_tokens == 100
    kwargs = client.models.generate_content.call_args.kwargs
    config = kwargs["config"]
    assert config.response_mime_type == "application/json"
    assert config.max_output_tokens == 65535
    assert config.thinking_config.thinking_budget == 1234
    contents = kwargs["contents"]
    assert [p.text for p in contents if p.text] == ["PROMPT", "FILE: home.png"]
    assert [p.inline_data.mime_type for p in contents if p.inline_data] == ["image/png"]


def test_generate_json_reports_truncation(monkeypatch):
    service, _ = _service(monkeypatch, _response('{"a": ', finish="MAX_TOKENS", thoughts=60000))
    with pytest.raises(TruncatedResponseError) as error:
        service.generate_json("PROMPT")
    assert error.value.result.thoughts_tokens == 60000
    assert "reasoning 60,000" in str(error.value)


def test_generate_json_reports_blocked_answers(monkeypatch):
    service, _ = _service(monkeypatch, _response("", finish="SAFETY"))
    with pytest.raises(IncompleteResponseError, match="SAFETY"):
        service.generate_json("PROMPT")


def test_generate_json_waits_and_retries_on_quota(monkeypatch):
    from google.genai import errors

    quota = errors.ClientError(429, {"error": {"code": 429, "message": "quota", "status": "x"}})
    service, client = _service(monkeypatch, quota, _response("{}"))
    messages = []
    assert service.generate_json("PROMPT", on_status=messages.append).text == "{}"
    assert client.models.generate_content.call_count == 2
    service._sleep.assert_called_once_with(20)
    assert "quota reached" in messages[0]


def test_generate_json_does_not_retry_other_client_errors(monkeypatch):
    from google.genai import errors

    bad = errors.ClientError(400, {"error": {"code": 400, "message": "bad", "status": "x"}})
    service, client = _service(monkeypatch, bad)
    with pytest.raises(errors.ClientError):
        service.generate_json("PROMPT")
    assert client.models.generate_content.call_count == 1


# ---------------------------------------------------------------- UI prompt

REQUIREMENTS = '{"requirements": [{"source_id": "ONP-1 Story.md"}]}'


def test_ui_prompt_lists_files_pdf_text_and_requirements(tmp_path):
    files = [
        UiFile("home.png", PNG, "image/png"),
        UiFile("flow.pdf", b"%PDF", "application/pdf", 2, "[Pagina 1]\nConferma"),
    ]
    prompt = build_ui_prompt(files, REQUIREMENTS, output_file=tmp_path / "ui.md")
    assert "- home.png (immagine PNG)" in prompt
    assert "- flow.pdf (PDF, 2 pagine)" in prompt
    assert "# FILE: flow.pdf\n\n[Pagina 1]\nConferma" in prompt
    assert REQUIREMENTS in prompt
    assert (tmp_path / "ui.md").read_text(encoding="utf-8") == prompt


def test_ui_prompt_requires_files_and_requirements(tmp_path):
    with pytest.raises(PromptBuildError):
        build_ui_prompt([], REQUIREMENTS, output_file=tmp_path / "ui.md")
    with pytest.raises(PromptBuildError):
        build_ui_prompt([UiFile("a.png", PNG, "image/png")], " ", output_file=tmp_path / "ui.md")
