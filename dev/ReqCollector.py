from __future__ import annotations

from pathlib import Path

# Directory principale del progetto e cartella che contiene i documenti Confluence.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_CONFLUENCE = PROJECT_ROOT / "data" / "input" / "confluence"


class MarkdownReader:
    """Legge i file Markdown di una cartella e li unisce in un unico testo."""

    def __init__(self):
        # Una stringa è considerata il nome di una sottocartella di Confluence;
        # un Path viene invece usato direttamente come percorso completo.
        self.directory = DATA_CONFLUENCE


    @staticmethod
    def format_document(name: str, text: str) -> str:
        """Racchiude il testo di un documento nei delimitatori FILE / FINE FILE."""
        return f"""
# FILE: {name}

{text}

# FINE FILE: {name}
"""

    def read_all(self) -> str:
        """Legge tutti i file .md presenti nella directory e restituisce il contenuto in un'unica stringa."""

        # Controlla che il percorso esista e sia effettivamente una directory.
        if not self.directory.exists():
            raise FileNotFoundError(
                f"Directory non trovata: {self.directory}"
            )

        if not self.directory.is_dir():
            raise NotADirectoryError(
                f"Il percorso non è una directory: {self.directory}"
            )

        # Accumula i contenuti nell'ordine alfabetico dei nomi dei file,
        # così il risultato è riproducibile tra esecuzioni.
        contents = []

        for file_path in sorted(self.directory.glob("*.md")):
            # Legge il file come testo UTF-8 e lo racchiude in delimitatori
            # per rendere riconoscibili i confini tra documenti.
            text = file_path.read_text(encoding="utf-8")

            contents.append(self.format_document(file_path.name, text))

        # Segnala esplicitamente se la directory non contiene file Markdown.
        if not contents:
            raise ValueError(
                f"Nessun file .md trovato in: {self.directory}"
            )

        # Restituisce tutti i documenti uniti da una riga vuota.
        return "\n".join(contents)
