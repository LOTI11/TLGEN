"""Esportazione dei test case nel file Excel/XLSM (usa dev/import_test_cases_xlsm.py)."""

from __future__ import annotations

from pathlib import Path

from dev import import_test_cases_xlsm

XLSM_MIME_TYPE = "application/vnd.ms-excel.sheet.macroEnabled.12"
_MAX_ERROR_LENGTH = 600


class ExportError(Exception):
    """L'importazione dei test case nel file XLSM non è riuscita."""


def export_test_list() -> Path:
    """Importa i test case nel template XLSM e restituisce il percorso del file generato."""
    output_file = import_test_cases_xlsm.XLSM_OUTPUT_FILE
    try:
        import_test_cases_xlsm.import_test_cases()
    except PermissionError as exc:
        raise ExportError(
            f"Impossibile scrivere {output_file.name}: chiudi il file se è aperto in Excel ({exc})."
        ) from exc
    except Exception as exc:  # JSON non valido, validazione pydantic, template/foglio mancanti, ...
        message = str(exc).strip() or type(exc).__name__
        if len(message) > _MAX_ERROR_LENGTH:
            message = message[:_MAX_ERROR_LENGTH] + "…"
        raise ExportError(f"Errore durante l'importazione dei test case: {message}") from exc

    if not output_file.is_file():
        raise ExportError(f"File di output non trovato dopo l'esportazione: {output_file}")
    return output_file
