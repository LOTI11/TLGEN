import os
import time
from collections.abc import Sequence
from pathlib import Path
from typing import Any

# Carica le impostazioni dal file .env, se presente.
from dotenv import load_dotenv
# SDK Google per chiamare Gemini tramite Vertex AI e leggere le credenziali.
from google import genai
from google.genai import errors, types
from google.oauth2 import service_account

from services.llm_types import (
    Attachment,
    IncompleteResponseError,
    LlmResult,
    StatusCallback,
    TruncatedResponseError,
)

# Massimo di token in uscita di Gemini 2.5 Flash (ragionamento incluso).
MAX_OUTPUT_TOKENS = 65535
# Attese (secondi) prima di ripetere una chiamata rifiutata per quota (429) o
# per indisponibilità temporanea del servizio (500/503).
RETRY_DELAYS = (20, 40, 60, 90, 120)
_RETRYABLE_CODES = {429, 500, 503}


class GeminiService:
    """Configura il client Vertex AI e permette di inviare prompt a Gemini."""

    def __init__(
        self,
        credentials_path: str | Path | None = None,
        project_id: str | None = None,
        location: str | None = None,
        model: str | None = None,
    ) -> None:
        load_dotenv()

        # Il percorso delle credenziali può essere passato al costruttore
        # oppure letto dalla variabile GOOGLE_APPLICATION_CREDENTIALS.
        credentials_file = credentials_path or os.getenv(
            "GOOGLE_APPLICATION_CREDENTIALS"
        )
        if credentials_file is None:
            raise ValueError(
                "Imposta GOOGLE_APPLICATION_CREDENTIALS o specifica credentials_path."
            )

        # Legge il JSON del service account e richiede lo scope necessario
        # per accedere ai servizi Google Cloud, inclusa Vertex AI.
        credentials = service_account.Credentials.from_service_account_file(
            str(credentials_file),
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )

        # Usa, in ordine, il progetto passato esplicitamente, quello configurato
        # nell'ambiente oppure il project_id presente nel JSON delle credenziali.
        resolved_project_id = (
            project_id or os.getenv("GOOGLE_CLOUD_PROJECT") or credentials.project_id
        )
        if resolved_project_id is None:
            raise ValueError(
                "Imposta GOOGLE_CLOUD_PROJECT o specifica project_id."
            )

        # Se non specificati, modello e località vengono letti dall'ambiente
        # o impostati ai valori predefiniti.
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

        # Crea il client Google configurato per Vertex AI e per il progetto,
        # la località e le credenziali selezionate sopra.
        self.client = genai.Client(
            vertexai=True,
            project=resolved_project_id,
            location=location or os.getenv("GOOGLE_CLOUD_LOCATION", "europe-west1"),
            credentials=credentials,
        )

    def generate_response(self, prompt: str) -> str:
        # Evita di inviare richieste prive di contenuto utile.
        if not prompt.strip():
            raise ValueError("Il prompt non può essere vuoto.")

        # Invia il prompt al modello configurato.
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        # Segnala esplicitamente il caso in cui Gemini non restituisca testo.
        if response.text is None:
            raise RuntimeError("Gemini non ha restituito testo.")

        # Restituisce al chiamante il testo generato da Gemini.
        return response.text

    def generate_response_with_files(
        self, prompt: str, files: Sequence[tuple[str, bytes, str]]
    ) -> str:
        """Invia il prompt insieme a dei file (immagini, PDF) nella stessa richiesta.

        ``files`` contiene tuple (nome, contenuto, mime type). Ogni file è
        preceduto da una riga "FILE: nome" così il modello può citarlo.
        """
        if not prompt.strip():
            raise ValueError("Il prompt non può essere vuoto.")
        if not files:
            raise ValueError("Nessun file da inviare.")

        response = self.client.models.generate_content(
            model=self.model, contents=self._contents(prompt, files)
        )
        if response.text is None:
            raise RuntimeError("Gemini non ha restituito testo.")
        return response.text

    @staticmethod
    def _contents(prompt: str, files: Sequence[Attachment]) -> list[types.Part]:
        contents: list[types.Part] = [types.Part.from_text(text=prompt)]
        for name, data, mime_type in files:
            contents.append(types.Part.from_text(text=f"FILE: {name}"))
            contents.append(types.Part.from_bytes(data=data, mime_type=mime_type))
        return contents

    def generate_json(
        self,
        prompt: str,
        *,
        files: Sequence[Attachment] = (),
        schema: Any = None,
        thinking_budget: int | None = None,
        on_status: StatusCallback | None = None,
    ) -> LlmResult:
        """Chiede una risposta JSON e verifica che sia completa.

        - ``schema`` (modello Pydantic) obbliga la risposta ad avere quei campi e valori;
        - ``thinking_budget`` limita i token di ragionamento, che altrimenti consumano
          il massimo di token in uscita;
        - se la risposta è troncata solleva ``TruncatedResponseError`` (il chiamante
          divide il lavoro), se è bloccata ``IncompleteResponseError``;
        - quota esaurita (429) o servizio non disponibile (500/503): attende e riprova.
        """
        if not prompt.strip():
            raise ValueError("Il prompt non può essere vuoto.")
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=schema,
            max_output_tokens=MAX_OUTPUT_TOKENS,
            thinking_config=(
                types.ThinkingConfig(thinking_budget=thinking_budget)
                if thinking_budget is not None
                else None
            ),
        )
        contents = self._contents(prompt, files) if files else prompt

        for attempt, delay in enumerate((*RETRY_DELAYS, None), start=1):
            try:
                response = self.client.models.generate_content(
                    model=self.model, contents=contents, config=config
                )
                break
            except errors.APIError as exc:
                if exc.code not in _RETRYABLE_CODES or delay is None:
                    raise
                if on_status:
                    reason = "quota reached" if exc.code == 429 else f"service error {exc.code}"
                    on_status(f"Gemini {reason}: waiting {delay}s (retry {attempt})…")
                self._sleep(delay)

        return self._result(response)

    _sleep = staticmethod(time.sleep)

    @staticmethod
    def _result(response: Any) -> LlmResult:
        candidate = (response.candidates or [None])[0]
        finish = getattr(candidate, "finish_reason", None)
        finish_name = getattr(finish, "name", None) or (str(finish) if finish else "STOP")
        usage = response.usage_metadata
        result = LlmResult(
            text=response.text or "",
            finish_reason=finish_name,
            prompt_tokens=getattr(usage, "prompt_token_count", None),
            output_tokens=getattr(usage, "candidates_token_count", None),
            thoughts_tokens=getattr(usage, "thoughts_token_count", None),
        )
        if finish_name == "MAX_TOKENS":
            raise TruncatedResponseError(result)
        if finish_name not in ("STOP", "FINISH_REASON_UNSPECIFIED") or not result.text.strip():
            raise IncompleteResponseError(
                f"Gemini non ha completato la risposta (motivo: {finish_name}; {result.usage()})."
            )
        return result
