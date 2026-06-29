from core.runtime import require_project_venv

require_project_venv()

from core.create_table import run


if __name__ == "__main__":
    run()
