import ast
import importlib
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]


def _registered_view_modules(register_path: Path) -> list[str]:
    if not register_path.exists():
        return []

    tree = ast.parse(register_path.read_text(encoding="utf-8"))
    modules: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and node.module.endswith(".views"):
            modules.append(node.module)

    return modules


def _model_candidates(view_module: str) -> list[str]:
    parts = view_module.split(".")
    if len(parts) < 3 or parts[-1] != "views":
        return []

    if parts[:2] == ["modules", "website"] and len(parts) >= 4:
        module_name = parts[2]
        return [
            f"modules.{module_name}.models",
            ".".join(parts[:-1] + ["models"]),
        ]

    return [".".join(parts[:-1] + ["models"])]


def import_registered_module_models() -> None:
    register_files = [
        ROOT_DIR / "core" / "api" / "register.py",
        ROOT_DIR / "modules" / "register.py",
        ROOT_DIR / "modules" / "website" / "register.py",
    ]

    imported: set[str] = set()
    for register_file in register_files:
        for view_module in _registered_view_modules(register_file):
            for model_module in _model_candidates(view_module):
                if model_module in imported:
                    continue
                try:
                    importlib.import_module(model_module)
                except ModuleNotFoundError as exc:
                    if exc.name != model_module:
                        raise
                    continue
                imported.add(model_module)
