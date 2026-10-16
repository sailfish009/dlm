import json
import subprocess
import sys
from pathlib import Path

import pytest

from dlm import (Atom, IRValidationError, Store, call_facts, field, lower_paths,
                 validate_pyir)


def test_python_lowers_to_typed_hierarchical_graph(tmp_path):
    source = tmp_path / "sample.py"
    source.write_text("def a(x):\n    return b(x)\n\ndef b(x):\n    return c(x)\n\ndef c(x):\n    return x\n")
    package = lower_paths((source,), tmp_path)
    validate_pyir(package)
    facts = call_facts(package)
    assert Atom("calls", ("sample.a", "sample.b")) in facts
    assert Atom("calls", ("sample.b", "sample.c")) in facts
    assert field(package, "nodes")[1][0] == "py-node"


def test_pyir_rejects_dangling_edge(tmp_path):
    source = tmp_path / "sample.py"
    source.write_text("def a():\n    return a()\n")
    package = lower_paths((source,), tmp_path)
    bad = package[:-1] + (("edges", ("py-edge", ("kind", "call"),
                                     ("from", "@missing"), ("to", "@missing"))),)
    with pytest.raises(IRValidationError):
        validate_pyir(bad)


def test_axiom_experiment():
    from experiments.axiom.run import execute
    result = execute()
    assert result["all_ok"], result


def test_ir_selfssl_is_recursive_event_driven_and_resumable(tmp_path):
    root = Path(__file__).resolve().parents[1]
    store_path = tmp_path / "store"
    cache_path = tmp_path / "cache"
    runner = root / "experiments/selfssl/run.py"
    command = [sys.executable, str(runner), "--rounds", "4", "--interval", "0",
               "--store", str(store_path), "--cache", str(cache_path),
               "--budget", "256", "--offline"]
    first = subprocess.run(command, cwd=root, text=True, capture_output=True,
                           check=True, timeout=30)
    state = Store(store_path).load()
    metrics = field(state, "metrics")
    events = field(state, "events")[1:]
    assert first.stdout.count("I improved my IR model") == len(events) >= 2
    assert field(metrics, "held-coverage")[1] == field(metrics, "held-total")[1] > 0
    assert field(metrics, "held-false")[1] == 0
    assert field(state, "round")[1] == 4
    acquisitions = field(field(state, "agenda"), "acquisitions")[1:]
    assert acquisitions
    assert all(field(record, "status")[1] in {"acquired", "abstained"}
               for record in acquisitions)
    assert json.loads((store_path / "snapshot.ir.json").read_text())[0] == "model-state"
    assert (store_path / "experience.irlog").read_text().strip()

    resumed = subprocess.run(
        [sys.executable, str(runner), "--rounds", "1", "--interval", "0",
         "--store", str(store_path), "--cache", str(cache_path),
         "--budget", "32", "--offline"],
        cwd=root, text=True, capture_output=True, check=True, timeout=30)
    assert "I improved my IR model" not in resumed.stdout
