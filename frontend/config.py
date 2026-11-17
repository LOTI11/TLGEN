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

STEPS: tuple[str, ...] = ("Documents", "Initiative", "Test Data", "Review", "Generation")

REVIEW_STEP = 3
PROGRESS_STEP = 4

# Backend pipeline stages shown in the progress screen: (key, label, description)
PIPELINE_STAGES: tuple[tuple[str, str, str], ...] = (
    ("inputs", "Prepare inputs", "Documents and user data"),
    ("prompt1", "Write prompt 1", "Requirements extraction prompt"),
    ("requirements", "Generate requirements", "Requirements JSON"),
    ("prompt2", "Write prompt 2", "Test case generation prompt"),
    ("test_cases", "Generate test cases", "Test case JSON"),
    ("export", "Build Test List", "Python → Excel/XLSM"),
)
