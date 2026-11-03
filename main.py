import json
import subprocess
import sys
from pathlib import Path

from dev import import_test_cases_xlsm
from services.gemini_service import GeminiService


def install_dependencies() -> None:
    requirements_file = Path(__file__).resolve().parent / "requirements.txt"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "-r",
            str(requirements_file),
        ],
        check=True,
    )


def main() -> None:
    #creazione istanza per gemini e comunicazione con il modello per generare una risposta
    #print("creazione istanza gemini")
    #gemini = GeminiService()

    #generazione risposta dal modello gemini
    #risposta = gemini.generate_response("scrivimi un testo di esempio")
    #print(risposta)

    #inserimento dei test case generati nel file template cliente
    import_test_cases_xlsm.import_test_cases()
    print("fine")


if __name__ == "__main__":
    install_dependencies()
    main()
