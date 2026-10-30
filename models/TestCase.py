from enum import Enum
from typing import Optional, Union
from pydantic import BaseModel, Field


class StepType(str, Enum):
    ATTIVITA_PRELIMINARI_PRECONDIZIONI = "Attività Preliminari e/o Precondizioni"
    STATO_BASE = "Stato Base"
    AZIONE = "Azione"
    VERIFICA_INTERNA = "Verifica interna"
    VERIFICA_ESTERNA = "Verifica esterna"


class TestStep(BaseModel):
    step_number: Union[int, str]
    step_type: StepType
    step_name: str
    actions_and_data: str
    expected_result: str


class TestCase(BaseModel):

    # iniziativa
    initiative_id: str
    application_module: Optional[str] = None
    user_requirement_id: Optional[str] = None

    # scomposizione base di test
    id1: Optional[str] = None
    macro_area: Optional[str] = None
    id2: Optional[str] = None
    requirement_use_case: str
    id3: str
    scenario_functionality: str
    scenario_test_case: Optional[str] = None

    #caso di test alto livello
    test_case_title: str
    test_case_macro_funzionalita: Optional[str] = None
    description_notes: Optional[str] = None
    test_type: str
    level: str
    estimated_duration: str

    # Step del caso di test
    steps: list[TestStep] = Field(default_factory=list)