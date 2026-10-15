"""Source code -> function-free binary Horn facts (stdlib ``ast`` only).

The extraction is deliberately conservative and label-free: it turns a Python
source tree into the **module import graph**, the one code relation that is both
mechanically trustworthy and non-trivial (a build/import graph is what a build
system actually needs, and its transitive closure is a real derived relation).

Node = a repo-relative dotted module name (``pkg.sub.mod``; ``__init__`` folded
into its package).  Edge ``(imports M N)`` when module ``M`` imports a repo
module ``N``.  Imports that resolve outside the repo (stdlib/third-party) are
dropped: the universe is the repo, exactly like the web experiment's entity set.
"""
from __future__ import annotations

import ast
import warnings
from typing import Dict, List, Sequence, Tuple

try:
    from .code import Fact
except ImportError:  # run as a top-level script
    from code import Fact


def module_name(path: str) -> Tuple[str, bool]:
    """Repo-relative path -> (dotted module, is_package).

    The first path component (repo-branch dir from the tarball) is dropped.
    """
    p = path.split("/", 1)[1] if "/" in path else path
    is_pkg = p.endswith("/__init__.py")
    if p.endswith(".py"):
        p = p[:-3]
    if p.endswith("/__init__"):
        p = p[:-len("/__init__")]
    return p.replace("/", ".").strip("."), is_pkg


def _module_index(files: Sequence[str]) -> Tuple[Dict[str, str], Dict[str, bool]]:
    mods: Dict[str, str] = {}
    is_pkg: Dict[str, bool] = {}
    for path in files:
        m, pkg = module_name(path)
        mods[path] = m
        is_pkg[m] = pkg
    return mods, is_pkg


def _resolve(dotted: str, names: set) -> str | None:
    """Deepest repo module that ``dotted`` names (or that names ``dotted``)."""
    if not dotted:
        return None
    prefix = [m for m in names if dotted == m or dotted.startswith(m + ".")]
    if prefix:
        return max(prefix, key=len)
    contained = [m for m in names if m.startswith(dotted + ".")]
    return min(contained, key=len) if contained else None


def import_edges(files: Dict[str, str]) -> List[Tuple[str, str]]:
    """(subj module, obj module) direct import edges, sorted & deduped."""
    mods, is_pkg = _module_index(list(files))
    names = set(mods.values())
    edges: set = set()
    for path, src in files.items():
        M = mods[path]
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", SyntaxWarning)
                tree = ast.parse(src)
        except (SyntaxError, ValueError, RecursionError):
            continue
        for node in ast.walk(tree):
            targets: List[str] = []
            if isinstance(node, ast.Import):
                targets = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    base = M if is_pkg.get(M) else M.rsplit(".", 1)[0]
                    parts = base.split(".") if base else []
                    up = node.level - 1
                    base = ".".join(parts[: len(parts) - up]) if up <= len(parts) else ""
                else:
                    base = ""
                if node.module:
                    targets = [(base + "." + node.module).strip(".")]
                elif node.level:
                    # ``from . import sub`` -> the submodule(s), not the package itself
                    targets = [(base + "." + a.name).strip(".") for a in node.names]
                else:
                    targets = []
            for dotted in targets:
                node_m = _resolve(dotted, names)
                if node_m and node_m != M:
                    edges.add((M, node_m))
    return sorted(edges)


def repo_facts(files: Dict[str, str], *, prefix: str = "") -> List[Fact]:
    """Import edges as ``(imports M N)`` facts, constants namespaced by ``prefix``."""
    p = (prefix + "_") if prefix else ""
    return [Fact("imports", p + s, p + o) for s, o in import_edges(files)]