import json
import subprocess
import sys
from pathlib import Path


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

    print("prova partenza")


if __name__ == "__main__":
    install_dependencies()
    main()
