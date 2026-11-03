# TLGEN

## Gemini su Vertex AI

Il servizio `GeminiService` invia un prompt a Gemini tramite Vertex AI usando
un account di servizio Google.

1. Salva il JSON dell'account di servizio in un percorso locale non versionato.
   Usa i valori JSON effettivi, non i collegamenti Markdown mostrati in eventuali
   esempi.
2. Copia `.env.example` in `.env` e imposta il percorso del JSON, l'ID del
   progetto Google Cloud e, se necessario, località e modello.
3. Abilita Vertex AI nel progetto, assegna all'account di servizio il ruolo
   Vertex AI User e installa le dipendenze con `pip install -r requirements.txt`.
4. Usa il servizio:

```python
from services.gemini_service import GeminiService

gemini = GeminiService()
response = gemini.generate_response("Riassumi questo requisito.")
print(response)
```

In alternativa, puoi passare `credentials_path`, `project_id`, `location` e
`model` al costruttore. `generate_response(prompt)` restituisce il testo
prodotto dal modello e segnala prompt vuoti o risposte senza testo con
un'eccezione.
