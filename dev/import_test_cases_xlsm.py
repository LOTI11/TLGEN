from __future__ import annotations

import json
import shutil
from copy import copy
from enum import Enum
from pathlib import Path
from typing import Optional

from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet
from pydantic import ValidationError

from models.TestCase import TestCase

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_INPUT = PROJECT_ROOT / "data" / "input"

JSON_FILE = DATA_INPUT / "test_cases.json"
XLSM_TEMPLATE_FILE = DATA_INPUT / "Template_TL_OneApp.xlsm"
XLSM_OUTPUT_FILE = DATA_INPUT / "Export_TL_OneApp.xlsm"

SHEET_NAME: Optional[str] = "SpecificaDiTest"
START_ROW = 4

COPY_TEMPLATE_ROW_STYLE = True


def empty_if_none(value: object) -> object:
    """Scrive una cella vuota quando il valore JSON è null."""
    return "" if value is None else value


def enum_value(value: object) -> object:
    """Converte gli Enum nella relativa stringa prima della scrittura."""
    return value.value if isinstance(value, Enum) else empty_if_none(value)


def copy_row_style(ws: Worksheet, source_row: int, target_row: int) -> None:
    """Copia stile, altezza e protezione della riga modello senza copiarne i valori."""
    if source_row == target_row:
        return

    source_dimension = ws.row_dimensions[source_row]
    target_dimension = ws.row_dimensions[target_row]
    target_dimension.height = source_dimension.height
    target_dimension.hidden = source_dimension.hidden
    target_dimension.outlineLevel = source_dimension.outlineLevel

    for column in range(1, ws.max_column + 1):
        source = ws.cell(row=source_row, column=column)
        target = ws.cell(row=target_row, column=column)

        if source.has_style:
            target._style = copy(source._style)
        if source.number_format:
            target.number_format = source.number_format
        target.alignment = copy(source.alignment)
        target.protection = copy(source.protection)


def write_cells(ws: Worksheet, row: int, values_by_column: dict[str, object]) -> None:
    for column, value in values_by_column.items():
        ws[f"{column}{row}"] = enum_value(value)


def load_test_cases(json_path: Path) -> list[TestCase]:
    if not json_path.is_file():
        raise FileNotFoundError(f"File JSON non trovato: {json_path.resolve()}")

    with json_path.open("r", encoding="utf-8-sig") as file:
        raw_data = json.load(file)

    if not isinstance(raw_data, dict) or not isinstance(
        raw_data.get("test_cases"), list
    ):
        raise ValueError("Il JSON deve contenere una lista 'test_cases'.")

    return [TestCase.model_validate(item) for item in raw_data["test_cases"]]


def select_worksheet(workbook, sheet_name: Optional[str]) -> Worksheet:
    if sheet_name:
        if sheet_name not in workbook.sheetnames:
            raise ValueError(
                f"Foglio '{sheet_name}' non trovato. Fogli disponibili: "
                f"{', '.join(workbook.sheetnames)}"
            )
        return workbook[sheet_name]

    for worksheet in workbook.worksheets:
        if worksheet.sheet_state == "visible":
            return worksheet

    raise ValueError("Il workbook non contiene fogli visibili.")


def import_test_cases() -> None:
    if XLSM_TEMPLATE_FILE.suffix.lower() != ".xlsm":
        raise ValueError("Il file modello deve avere estensione .xlsm")
    if XLSM_OUTPUT_FILE.suffix.lower() != ".xlsm":
        raise ValueError("Il file di output deve avere estensione .xlsm")
    if not XLSM_TEMPLATE_FILE.is_file():
        raise FileNotFoundError(
            f"File Excel modello non trovato: {XLSM_TEMPLATE_FILE.resolve()}"
        )

    test_cases = load_test_cases(JSON_FILE)

    shutil.copy2(XLSM_TEMPLATE_FILE, XLSM_OUTPUT_FILE)

    workbook = load_workbook(XLSM_OUTPUT_FILE, keep_vba=True, keep_links=True)
    worksheet = select_worksheet(workbook, SHEET_NAME)

    current_row = START_ROW
    parent_count = 0
    step_count = 0

    for test_case in test_cases:
        if COPY_TEMPLATE_ROW_STYLE:
            copy_row_style(worksheet, START_ROW, current_row)

        write_cells(
            worksheet,
            current_row,
            {
                "A": test_case.initiative_id,
                "B": test_case.application_module,
                "C": test_case.user_requirement_id,
                "D": test_case.id1,
                "E": test_case.macro_area,
                "F": test_case.id2,
                "G": test_case.requirement_use_case,
                "I": test_case.id3,
                "J": test_case.scenario_functionality,
                "L": test_case.test_case_title,
                "M": test_case.description_notes,
                "N": test_case.scenario_functionality,
                "O": test_case.test_type,
                "R": test_case.estimated_duration,
                "AN": "TESTPADRE",
            },
        )
        parent_count += 1
        current_row += 1

        for step in test_case.steps:
            if COPY_TEMPLATE_ROW_STYLE:
                copy_row_style(worksheet, START_ROW, current_row)

            write_cells(
                worksheet,
                current_row,
                {
                    "T": step.step_number,
                    "U": step.step_type,
                    "V": step.step_name,
                    "W": step.actions_and_data,
                    "X": step.expected_result,
                    "AN": "TEST",
                },
            )
            step_count += 1
            current_row += 1

    workbook.save(XLSM_OUTPUT_FILE)
    workbook.close()

    print(f"File creato: {XLSM_OUTPUT_FILE.resolve()}")
    print(f"Test padre inseriti: {parent_count}")
    print(f"Step inseriti: {step_count}")
    print(f"Ultima riga utilizzata: {current_row - 1}")


if __name__ == "__main__":
    try:
        import_test_cases()
    except (FileNotFoundError, ValueError, json.JSONDecodeError, ValidationError) as error:
        raise SystemExit(f"ERRORE: {error}") from error
