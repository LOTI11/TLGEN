"""UI-level validation. Each function returns a list of user-facing errors."""

from __future__ import annotations

from frontend.config import INITIATIVE_LABELS
from frontend.state import AppState

__all__ = ["INITIATIVE_LABELS", "validate_step"]


def selected_document_count(state: AppState) -> int:
    return len(state.selected_repo_documents) + len(state.uploaded_documents)


def validate_documents(state: AppState) -> list[str]:
    if selected_document_count(state) == 0:
        return ["Select at least one document or upload a new one."]
    return []


def validate_initiative(state: AppState) -> list[str]:
    return [
        f"“{label}” is required."
        for key, label in INITIATIVE_LABELS.items()
        if not state.initiative[key].strip()
    ]


def validate_test_data(state: AppState) -> list[str]:
    if state.test_count < 1:
        return ["Enter the number of tests required (at least 1)."]
    return []


def validate_review(state: AppState) -> list[str]:
    return []


VALIDATORS = (
    validate_documents,
    validate_initiative,
    validate_test_data,
    validate_review,
)


def validate_step(state: AppState, step: int) -> list[str]:
    return VALIDATORS[step](state)
