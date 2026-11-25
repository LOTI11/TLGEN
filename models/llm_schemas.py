"""Schemi delle risposte richieste a Gemini nella generazione dei casi di test.

Vengono passati al modello come ``response_schema``: la risposta è JSON con
esattamente questi campi e questi valori ammessi. I campi di tracciabilità
(initiative_id, epic_id, ...) non sono qui perché li compila il codice a
partire dal requisito (vedi ``services.test_case_generation``).
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel

from models.TestCase import StepType


class CaseKind(str, Enum):
    FUNZIONALE = "Funzionale"
    INTEGRATO = "Integrato"


# --------------------------------------------------------------- fase A: elenco


class OutlineCase(BaseModel):
    """Un caso di test individuato, senza step."""

    requirement_ref: str  # riferimento del requisito nel prompt, es. "R2"
    test_case_title: str
    scenario_test_case: str
    test_type: CaseKind
    covered_conditions: list[str]  # condizioni verificate (acceptance criteria, regole, stati)


class OutlineResponse(BaseModel):
    test_cases: list[OutlineCase]


# --------------------------------------------------------------- fase B: step


class DetailStep(BaseModel):
    step_number: int
    step_type: StepType
    step_name: str
    actions_and_data: str
    expected_result: str


class DetailCase(BaseModel):
    case_ref: str  # riferimento del caso nel prompt, es. "C3"
    description_notes: str
    steps: list[DetailStep]


class DetailResponse(BaseModel):
    test_cases: list[DetailCase]
