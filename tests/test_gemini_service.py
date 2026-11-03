from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from services.gemini_service import GeminiService


def build_service(
    monkeypatch: pytest.MonkeyPatch, response_text: str | None
) -> GeminiService:
    # Simula il client Gemini: non invia richieste a Google e restituisce
    # il testo impostato dal test.
    client = Mock()
    client.models.generate_content.return_value = SimpleNamespace(text=response_text)

    # Sostituisce il caricamento del file di credenziali con credenziali finte.
    credentials = SimpleNamespace(project_id="test-project")
    load_credentials = Mock(return_value=credentials)
    monkeypatch.setattr(
        "services.gemini_service.service_account.Credentials.from_service_account_file",
        load_credentials,
    )
    monkeypatch.setattr(
        "services.gemini_service.genai.Client",
        Mock(return_value=client),
    )

    # Fornisce al servizio un percorso fittizio, che non viene letto perché
    # la funzione che carica le credenziali è stata simulata sopra.
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")

    # Crea il servizio usando le dipendenze simulate.
    service = GeminiService()
    load_credentials.assert_called_once_with(
        "credentials.json",
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    return service


def test_generate_response_returns_model_text(monkeypatch: pytest.MonkeyPatch) -> None:
    # Verifica che il servizio restituisca il testo prodotto dal modello simulato.
    service = build_service(monkeypatch, "Risposta Gemini")

    assert service.generate_response("Spiega il requisito") == "Risposta Gemini"

    # Verifica che il prompt e il modello configurato siano passati al client.
    service.client.models.generate_content.assert_called_once_with(
        model="gemini-2.5-flash",
        contents="Spiega il requisito",
    )


@pytest.mark.parametrize("prompt", ["", "   "])
def test_generate_response_rejects_empty_prompt(
    monkeypatch: pytest.MonkeyPatch, prompt: str
) -> None:
    # Prova sia una stringa vuota sia una contenente solo spazi.
    service = build_service(monkeypatch, "Risposta Gemini")

    # Il servizio deve rifiutare il prompt prima di chiamare Gemini.
    with pytest.raises(ValueError, match="prompt non può essere vuoto"):
        service.generate_response(prompt)


def test_generate_response_errors_when_model_returns_no_text(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Simula una risposta del modello senza testo.
    service = build_service(monkeypatch, None)

    # Il servizio deve segnalare esplicitamente che manca il testo.
    with pytest.raises(RuntimeError, match="non ha restituito testo"):
        service.generate_response("Ciao")
