from pydantic import BaseModel, Field
from typing import Optional

class SourceType(str, Enum):
    PDF = "PDF"
    DOCX = "DOCX"

class Requirement(BaseModel):
    # Documento da cui proviene il requisito
    source: SourceType

    # ID opzionale del documento
    source_id: Optional[str] = None

    # Riferimenti
    iniziativa_id: Optional[str] = None
    epic_id: Optional[str] = None
    jira_id: Optional[str] = None
    confluence_id: Optional[str] = None

    # Requisito
    title: str
    description: str

    acceptance_criteria: list[str] = Field(default_factory=list)
    business_rules: list[str] = Field(default_factory=list)

    systems: list[str] = Field(default_factory=list)
    platforms: list[str] = Field(default_factory=list)

    source_reference: Optional[str] = None