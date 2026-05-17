import importlib.util
from pathlib import Path


def test_main_entrypoint_imports_without_running_training():
    main_path = Path(__file__).resolve().parents[1] / "main.py"
    spec = importlib.util.spec_from_file_location("main_entrypoint", main_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert module is not None
