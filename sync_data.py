from core.runtime import require_project_venv
from core.sync_data import run

require_project_venv()
if __name__ == "__main__":
    run()
