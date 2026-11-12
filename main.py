import json
import subprocess
import sys
from pathlib import Path

from dev import import_test_cases_xlsm
from dev import ReqCollector
from services.gemini_service import GeminiService

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_PROMPT = PROJECT_ROOT / "parser" / "prompt"
DATA_FINAL_PROMPT = PROJECT_ROOT / "parser" / "finalPrompt"
DATA_JSON = PROJECT_ROOT / "data" / "input" / "jsonAI"


FILE_JSON_REQUIREMENTS = DATA_JSON / "requirements.json"
FILE_PROMPT_REQUIREMENTS = DATA_PROMPT / "parser.md"
FILE_FINAL_PROMPT_REQUIREMENTS = DATA_FINAL_PROMPT / "finalParser.md"

FILE_JSON_TEST_CASES = DATA_JSON / "test_cases.json"
FILE_PROMPT_TEST_CASES = DATA_PROMPT / "testCaseGenerator.md"
FILE_FINAL_PROMPT_TEST_CASES = DATA_FINAL_PROMPT / "finalTestCases.md"

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
    # Legge i file Markdown dalla cartella locale di Confluence.
    print("Raccolta requisiti da repository locale")
    requirements_text = ReqCollector.MarkdownReader().read_all()
    print("Documenti raccolti")

    #preparazione prompt requisiti -> merge tra il prompt e la parte funzionale dei requisiti raccolti dai file markdown
    file_prompt_requirements_text = FILE_PROMPT_REQUIREMENTS.read_text(encoding="utf-8")
    prompt_requirements_finale = file_prompt_requirements_text + "\n\n" + requirements_text
    FILE_FINAL_PROMPT_REQUIREMENTS.write_text(prompt_requirements_finale, encoding="utf-8")
    print("Prompt requisiti generato")


    #creazione istanza per gemini e comunicazione con il modello per generare una risposta
    print("creazione istanza gemini")
    gemini = GeminiService()

    #generazione risposta dal modello gemini -> preparazione del file json con i requisiti raccolti e parsati
    responseRequirements = gemini.generate_response(prompt_requirements_finale)
    
    #inserimento della risposta generata dal modello gemini nel file requirements.json (con appoggio ad un file di testo per formattazione)
    #inserimento nel file di testo per formattazione e controllo sui caratteri
    righe = responseRequirements.strip().splitlines()
    if righe and righe[0].strip().lower() == "```json":
        if righe[-1].strip() != "```":
            raise ValueError("La risposta JSON inizia con ```json ma non termina con ```")
        risposta_pulita = "\n".join(righe[1:-1]).strip()
    else:
        risposta_pulita = responseRequirements.strip()

    path_file = Path(__file__).resolve().parent / "data" / "input" / "prova.txt"
    path_file.write_text(risposta_pulita, encoding="utf-8")

    # inserimento e salvataggio del file json con i requisiti raccolti e parsati
    risposta_req_json = json.loads(risposta_pulita)
    with FILE_JSON_REQUIREMENTS.open("w", encoding="utf-8") as file:
        json.dump(
            risposta_req_json,
            file,
            indent=4,
            ensure_ascii=False
        )

    #preparazione prompt testcases -> merge tra il prompt e la parte funzionale dei requisiti raccolti dai file markdown
    file_prompt_test_cases_text = FILE_PROMPT_TEST_CASES.read_text(encoding="utf-8")
    prompt_test_cases_finale = file_prompt_test_cases_text + "\n\n" + FILE_JSON_REQUIREMENTS.read_text(encoding="utf-8")
    FILE_FINAL_PROMPT_TEST_CASES.write_text(prompt_test_cases_finale, encoding="utf-8")
    print("Prompt test case generato")
    
    #generazione risposta dal modello gemini -> preparazione del file json con i requisiti raccolti e parsati
    responseTestCases = gemini.generate_response(prompt_test_cases_finale)

    #inserimento della risposta generata dal modello gemini nel file test_cases.json (con appoggio ad un file di testo per formattazione)
    #inserimento nel file di testo per formattazione e controllo sui caratteri
    righe = responseTestCases.strip().splitlines()
    if righe and righe[0].strip().lower() == "```json":
        if righe[-1].strip() != "```":
            raise ValueError("La risposta JSON inizia con ```json ma non termina con ```")
        risposta_pulita_test = "\n".join(righe[1:-1]).strip()
    else:
        risposta_pulita_test = responseTestCases.strip()

    path_file_test = Path(__file__).resolve().parent / "data" / "input" / "provaTest.txt"
    path_file_test.write_text(risposta_pulita_test, encoding="utf-8")
    
    #inserimento e salvataggio del file json con i requisiti raccolti e parsati
    risposta_test_cases_json = json.loads(risposta_pulita_test)
    with FILE_JSON_TEST_CASES.open("w", encoding="utf-8") as file:
        json.dump(
            risposta_test_cases_json,
            file,
            indent=4,
            ensure_ascii=False
        )
    

    #inserimento dei test case generati nel file template cliente
    print("importazione test case nel file xlsm")
    try:
        import_test_cases_xlsm.import_test_cases()
        print("inserimento completato")
    except Exception as e:
        print(f"Errore durante l'importazione dei test case: {e}")
    

if __name__ == "__main__":
    install_dependencies()
    main()
