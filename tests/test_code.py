"""Network-free tests of the v0.0039 code experiment + import extraction."""
import argparse

from experiments.code.extract import import_edges, module_name
from experiments.code.run import run


def _args(**over):
    base = dict(repos=4, per_repo=12, seed=1, offline=True, synthetic=True,
                cache="/tmp/dlm_code_test_cache", pages=1, max_files=50,
                max_file_bytes=100_000, train_frac=0.6, max_body=2, max_neg=1000,
                pause=0.0, retries=0, json="")
    base.update(over)
    return argparse.Namespace(**base)


FILES = {
    "repo-main/pkg/__init__.py": "from . import a\n",
    "repo-main/pkg/a.py": "import os\nfrom .b import f\n",
    "repo-main/pkg/b.py": "import a\n",
    "repo-main/main.py": "from pkg.a import f\n",
}


def test_module_name():
    assert module_name("repo-main/pkg/a.py") == ("pkg.a", False)
    assert module_name("repo-main/pkg/__init__.py") == ("pkg", True)


def test_import_edges_resolve_repo_modules_only():
    assert import_edges(FILES) == [("main", "pkg.a"), ("pkg", "pkg.a"), ("pkg.a", "pkg.b")]


def test_synthetic_learns_transitivity_and_beats_identity():
    out = run(_args())
    assert out["verdict"]["found_transitivity"]
    assert out["verdict"]["learned_sound"]
    assert out["verdict"]["learned_beats_identity"]
    assert out["arms"]["learned"]["held_recovery"] > out["arms"]["identity"]["held_recovery"] + 0.1


def test_synthetic_is_deterministic():
    a = run(_args())
    b = run(_args())
    assert a == b