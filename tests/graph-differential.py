"""Optional graph-engine oracle check; Python is not a graph runtime dependency."""
from pathlib import Path
import random
import re
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root.parent / "dlm_v0.0066"))
from dlm.kernel import Atom, Rule, closure

rng = random.Random(75)
base = Rule(Atom("reach", ("?x", "?y")), (Atom("edge", ("?x", "?y")),))
recursive = Rule(Atom("reach", ("?x", "?z")),
                 (Atom("reach", ("?x", "?y")), Atom("edge", ("?y", "?z"))))
program = """
(define x (dlm-var 'x))
(define y (dlm-var 'y))
(define z (dlm-var 'z))
(define oracle-rules (list
  (dlm-rule (dlm-atom 'reach x y) (dlm-atom 'edge x y))
  (dlm-rule (dlm-atom 'reach x z) (dlm-atom 'reach x y) (dlm-atom 'edge y z))))
"""
expected = []
for i in range(20):
    facts = {Atom("edge", (f"n{a}", f"n{b}")) for a in range(5)
             for b in range(5) if rng.random() < .18}
    expected.append(set(closure(facts, (base, recursive))))
    forms = " ".join(f"(dlm-atom 'edge '{a.args[0]} '{a.args[1]})" for a in sorted(facts))
    program += f"(define graph{i} (gr-from-episode (dlm-episode 'case{i} (list {forms}) () ()) oracle-rules 20))\n"
    program += f'(println "CASE{i} " (gr-closure graph{i}))\n'
    program += f"(list-do target (gr-closure graph{i}) (assert (= (dlm-nth (gr-query graph{i} target) 1) 'entailed) \"graph witness failed\"))\n"
process = subprocess.run([str(root / "scripts/run.sh"), "repl"], cwd=root,
                         input=program, text=True, capture_output=True, timeout=90, check=True)
found = {}
for line in process.stdout.splitlines():
    match = re.search(r"CASE(\d+) ", line)
    if match:
        found.setdefault(int(match[1]), {Atom(pred, (a, b)) for pred, a, b in re.findall(
            r"\(atom (\w+) \((\w+) (\w+)\)\)", line)})
assert len(found) == 20, process.stdout
for i, target in enumerate(expected):
    assert found[i] == target, (i, found[i] ^ target)
print("PASS: 20 seeded graph closures against Python0066; all graph witnesses checked")
