"""Frontend configuration."""

from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

APP_TITLE = "TLGEN"
APP_SUBTITLE = "Your Test List ready in minutes"

# Directory scanned for the "Available Documents" section.
# Override with the TLGEN_DOCUMENTS_DIR environment variable.
DOCUMENTS_DIR = Path(
    os.environ.get("TLGEN_DOCUMENTS_DIR", PROJECT_ROOT / "data" / "input" / "confluence")
)

SUPPORTED_EXTENSIONS: tuple[str, ...] = ("md",)

# Directory scanned for the "UI designs" tab (screens exported from Figma).
# Override with the TLGEN_UI_DIR environment variable.
UI_DOCUMENTS_DIR = Path(
    os.environ.get("TLGEN_UI_DIR", PROJECT_ROOT / "data" / "input" / "figma")
)

UI_EXTENSIONS: tuple[str, ...] = ("png", "pdf")

STEPS: tuple[str, ...] = ("Documents", "Initiative", "Test Data", "Review", "Generation")

REVIEW_STEP = 3
PROGRESS_STEP = 4

# Backend pipeline stages shown in the progress screen: (key, label, description)
PIPELINE_STAGES: tuple[tuple[str, str, str], ...] = (
    ("inputs", "Prepare inputs", "Documents and user data"),
    ("prompt1", "Write prompt 1", "Requirements extraction prompt"),
    ("requirements", "Generate requirements", "Requirements JSON"),
    ("ui", "Analyze UI designs", "Figma screens → UI spec JSON"),
    ("prompt2", "Plan test cases", "Split by user story"),
    ("test_cases", "Generate test cases", "Case list and steps per user story, checked"),
    ("export", "Build Test List", "Python → Excel/XLSM"),
)

# How the requested number of test cases is used: label shown -> value for the prompt.
TEST_COUNT_MODES: dict[str, str] = {"Indicativo": "indicativo", "Preciso": "preciso"}
DEFAULT_TEST_COUNT_MODE = "indicativo"
TEST_COUNT_MODE_HELP: dict[str, str] = {
    "indicativo": (
        "Il modello analizza i requisiti e decide quanti test servono per la copertura "
        "completa, senza essere condizionato dal numero indicato: può generarne meno o più."
    ),
    "preciso": (
        "Il modello genera esattamente il numero indicato, accorpando le condizioni affini o "
        "dando priorità ai flussi principali. Se i requisiti supportano meno casi, ne genera "
        "meno per non inventare o duplicare test."
    ),
}

# Initiative form fields: state key -> label.
INITIATIVE_LABELS: dict[str, str] = {
    "name": "Nome iniziativa",
    "id": "ID iniziativa",
    "epic": "Epica",
    "requirement_id": "ID requisito utente",
}
