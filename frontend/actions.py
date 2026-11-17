"""CTA handlers.

This is the single integration point with the backend. Business logic is NOT
implemented yet: when ready, call the existing services from
``on_generate_clicked`` (e.g. generate_requirements() -> generate_test_cases()
-> export_test_list()), reading inputs from ``get_state()`` and reporting
progress with ``set_stage_status(stage_key, status, message)``.
"""

from __future__ import annotations

from frontend.config import PROGRESS_STEP
from frontend.state import get_state, go_to


def on_generate_clicked() -> None:
    # TODO: connect backend pipeline here.
    get_state().generate_requested = True
    go_to(PROGRESS_STEP)
