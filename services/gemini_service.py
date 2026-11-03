import os
from pathlib import Path

# Carica le impostazioni dal file .env, se presente.
from dotenv import load_dotenv
# SDK Google per chiamare Gemini tramite Vertex AI e leggere le credenziali.
from google import genai
from google.oauth2 import service_account


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
