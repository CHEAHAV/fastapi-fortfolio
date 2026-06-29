import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
PROJECT_VENV = BASE_DIR / "venv"


def require_project_venv() -> None:
    current_prefix  = Path(sys.prefix).resolve()
    expected_prefix = PROJECT_VENV.resolve()

    if current_prefix == expected_prefix:
        return

    message = (
        "This project must be run with its Python 3.14 virtual environment.\n\n"
        f"Current Python: {current_prefix}\n"
        f"Required venv : {expected_prefix}\n\n"
        "Open the venv first"
    )
    sys.stderr.write(f"{message}\n")
    raise SystemExit(1)
