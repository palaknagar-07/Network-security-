import importlib


def test_main_entrypoint_imports_without_running_training():
    module = importlib.import_module("main")

    assert module is not None
