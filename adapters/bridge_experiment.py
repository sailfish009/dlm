"""Equal pair-budget routing ablation; runtime includes startup/cache maintenance.
Developer experiment only. No Python is used by the native learning loop.
"""
import json
from pathlib import Path
import random
import statistics
import subprocess
import tempfile
import time

from sexp import Symbol as S, dumps, loads_many

ROOT = Path(__file__).resolve().parents[1]


def run(seed, enabled):
    rng = random.Random(seed)
    facts_a = [[S('atom'), S('edge'), [S(a), S(b)]] for a, b in zip('abcd', 'bcde')]
    facts_b = [[S('atom'), S('edge'), [S(a), S(b)]] for a, b in zip('uvwx', 'vwxy')]
    rng.shuffle(facts_a)
    rng.shuffle(facts_b)
    code = f'''(dlm 'observe 'a '{dumps(facts_a)})
(dlm 'observe 'b '{dumps(facts_b)})
(set *dlm-pair-budget* 8)
(dlm 'ground '{'on' if enabled else 'off'})
(times-do 6 (dump (dlm 'step)) (print "\\n"))
(dump (list 'paths (a77-words (a77-defs *dlm-model*)))) (print "\\n")
(dump (list 'query (car (dlm 'query 'a '(atom "c77-0" (a c)))))) (print "\\n")
(dump (dlm 'ground)) (print "\\n")
'''
    with tempfile.NamedTemporaryFile(mode='w', suffix='.l') as driver:
        driver.write(code)
        driver.flush()
        start = time.perf_counter()
        proc = subprocess.run([str(ROOT / 'scripts/run.sh'), 'proof', driver.name],
                              capture_output=True, text=True, timeout=120)
        elapsed = time.perf_counter() - start
    if proc.returncode:
        raise RuntimeError(proc.stderr + proc.stdout)
    rows = loads_many(proc.stdout)
    return dict(seed=seed, routing=enabled, wall_seconds=elapsed,
                rounds=rows[:6], paths=rows[6][1], query=rows[7][1], ground=rows[8])


def main():
    results = [run(seed, enabled) for seed in (0, 1, 2) for enabled in (False, True)]
    report = dict(protocol='three shuffled explicit-source fixtures; six rounds x pair budget 8; one process per arm',
                  caveats=['pair budget is not a primitive/time bound',
                           'wall time includes startup, closure, proof verification and cache rebuilding',
                           'tiny in-domain fixture, no held-out generalization or efficiency claim'],
                  results=results,
                  median_wall_seconds={str(flag): statistics.median(r['wall_seconds'] for r in results
                                                                   if r['routing'] == flag)
                                       for flag in (False, True)})
    target = ROOT / 'docs/bridge83-experiment.json'
    target.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
