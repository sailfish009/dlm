"""DLM v0.0039 test: the trusted kernel's import boundary."""
import ast
import pathlib

KERNEL = pathlib.Path(__file__).resolve().parents[1] / "dlm" / "__init__.py"
ALLOWED = {"__future__", "dataclasses", "typing"}


def _imports(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    mods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            mods.add(node.module.split(".")[0])
        elif isinstance(node, ast.Import):
            for alias in node.names:
                mods.add(alias.name.split(".")[0])
    return mods


def test_kernel_imports_only_stdlib():
    assert _imports(KERNEL) <= ALLOWED


def test_kernel_never_imports_the_untrusted_layers():
    mods = _imports(KERNEL)
    assert not mods & {"dlm", "lisp", "ground", "ir", "proof", "abstract"}