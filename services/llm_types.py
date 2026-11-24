"""Tipi condivisi per le chiamate al modello (nessuna dipendenza dall'SDK Google)."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any, Protocol

# Allegato inviato con il prompt: (nome, contenuto, mime type).
Attachment = tuple[str, bytes, str]
StatusCallback = Callable[[str], None]


@dataclass(frozen=True)
class LlmResult:
    """Testo della risposta con il motivo di chiusura e i token usati."""

    text: str
    finish_reason: str = "STOP"
    prompt_tokens: int | None = None
    output_tokens: int | None = None
    thoughts_tokens: int | None = None

    def usage(self) -> str:
        parts = [
            f"{label} {value:,}"
            for label, value in (
                ("input", self.prompt_tokens),
                ("output", self.output_tokens),
                ("reasoning", self.thoughts_tokens),
            )
            if value is not None
        ]
        return "tokens: " + ", ".join(parts) if parts else "tokens: n/a"


class TruncatedResponseError(RuntimeError):
    """La risposta è stata interrotta perché ha raggiunto il massimo di token in uscita."""

    def __init__(self, result: LlmResult) -> None:
        super().__init__(
            f"Risposta del modello troncata (massimo di token in uscita raggiunto; {result.usage()})."
        )
        self.result = result


class IncompleteResponseError(RuntimeError):
    """Il modello non ha completato la risposta (blocco di sicurezza, contenuto vietato, ...)."""


class JsonLlmClient(Protocol):
    """Client che restituisce una risposta JSON completa o solleva un errore esplicito."""

    def generate_json(
        self,
        prompt: str,
        *,
        files: Sequence[Attachment] = (),
        schema: Any = None,
        thinking_budget: int | None = None,
        on_status: StatusCallback | None = None,
    ) -> LlmResult: ...
