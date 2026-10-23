"""Matched-round native search ablations; no Python proposer or policy.
Costs include startup, pool generation and controller maintenance (in-memory).
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


def sources(seed, workload):
    rng = random.Random(seed)
    episodes = []
    for prefix in ('a', 'b'):
        edges = [[S('atom'), S('edge'), [f'{prefix}{i}', f'{prefix}{i+1}']] for i in range(4)]
        if workload == 'distractors':
            noise = [[S('atom'), S('noise'), [f'{prefix}x{i}', f'{prefix}y{i}']] for i in range(16)]
            rng.shuffle(noise)
            edges = noise + edges
        else:
            # A low-reuse long path permits negative cache reuse after short
            # shared definitions are learned. Different episodes stay isolated.
            edges = [[S('atom'), S('edge'), [f'{prefix}{i}', f'{prefix}{i+1}']]
                     for i in range(4 if prefix == 'a' else 3)]
            rng.shuffle(edges)
        episodes.append(edges)
    return episodes


def run(seed, workload, mode, target=None):
    a, b = sources(seed, workload)
    code = f'''(dlm 'observe 'a '{dumps(a)})
(dlm 'observe 'b '{dumps(b)})
(set *dlm-pair-budget* 8)
'''
    if mode != 'legacy':
        code += f"(dlm 'search '{mode})\n"
    code += '''(define bench-calls84 0)
(define bench-original84 a77-certify)
(define-function bench-certify84 (model candidate)
  (set bench-calls84 (+ bench-calls84 1)) (bench-original84 model candidate))
(set a77-certify bench-certify84)
(set *a84-inspected* 0)
'''
    if mode == 'legacy':
        code += '(set *a84-counting* true)\n'
    if target is None:
        code += '''(times-do 6 (dump (dlm 'step)) (print "\\n"))\n'''
    else:
        code += f'''(define iterations84 0)
(while (and (< iterations84 128) (< (dlm-length (a77-defs *dlm-model*)) {target}))
  (dlm 'step) (set iterations84 (+ iterations84 1)))
(dump (list 'iterations iterations84)) (print "\\n")\n'''
    code += '''(dump (list 'paths (a77-words (a77-defs *dlm-model*)))) (print "\\n")
(dump (list 'valid (a77-valid? *dlm-model*) 'certify-calls bench-calls84)) (print "\\n")
(dump (dlm 'search)) (print "\\n")
(dump *s84-control*) (print "\\n")
'''
    with tempfile.NamedTemporaryFile(mode='w', suffix='.l') as driver:
        driver.write(code)
        driver.flush()
        start = time.perf_counter()
        proc = subprocess.run([str(ROOT / 'scripts/run.sh'), 'proof', driver.name],
                              text=True, capture_output=True, timeout=120)
        elapsed = time.perf_counter() - start
    if proc.returncode:
        raise RuntimeError(proc.stderr + proc.stdout)
    rows = loads_many(proc.stdout)
    n = 6 if target is None else 1
    if rows[n+1][1] != 'true':
        raise AssertionError(rows[n+1])
    return dict(seed=seed, workload=workload, mode=mode, wall_seconds=elapsed,
                rounds=rows[:n], paths=rows[n][1], certify_calls=rows[n+1][3], controller=rows[n+2],
                controller_serialized_bytes=len(dumps(rows[n+3]).encode()), target=target)


def main():
    results = []
    for workload in ('rare-path', 'distractors'):
        for seed in (0, 1, 2):
            for mode in ('legacy', 'cache', 'rank', 'ucb'):
                trials = [run(seed, workload, mode) for _ in range(3)]
                row = trials[0]
                for trial in trials[1:]:
                    assert trial['paths'] == row['paths'] and trial['rounds'] == row['rounds']
                row['wall_repeats'] = [t['wall_seconds'] for t in trials]
                row['wall_seconds'] = statistics.median(row['wall_repeats'])
                results.append(row)
    target_results = []
    for seed in (0, 1, 2):
        for mode in ('legacy', 'cache', 'rank', 'ucb'):
            trials = [run(seed, 'distractors', mode, target=2) for _ in range(3)]
            row = trials[0]
            row['wall_repeats'] = [t['wall_seconds'] for t in trials]
            row['wall_seconds'] = statistics.median(row['wall_repeats'])
            target_results.append(row)
    report = dict(time_to_target=target_results, protocol='two workloads x three seeds x four modes x three repeats; six rounds, budget8 per round; fresh native processes',
                  caveats=['budget counts legacy raw pair visits versus indexed candidate decisions: not equal primitive work',
                           'wall time includes process startup and all in-memory pool/cache/controller costs',
                           'persistent checkpoint replay is tested separately, not timed here',
                           'only complete insufficient-reuse outcomes are cached, never logical impossibility',
                           'cache mode also adds indexed joins and persistent frontier; UCB effect requires comparison to cache/rank'],
                  results=results)
    (ROOT / 'docs/search84-experiment.json').write_text(json.dumps(report, indent=2) + '\n')
    for workload in ('rare-path', 'distractors'):
        for mode in ('legacy', 'cache', 'rank', 'ucb'):
            rows = [r for r in results if r['workload'] == workload and r['mode'] == mode]
            print(workload, mode, 'definitions', [len(r['paths']) for r in rows],
                  'calls', [r['certify_calls'] for r in rows],
                  'median_seconds', round(statistics.median(r['wall_seconds'] for r in rows), 4))
    for mode in ('legacy', 'cache', 'rank', 'ucb'):
        rows = [r for r in target_results if r['mode'] == mode]
        print('target2', mode, 'rounds', [r['rounds'][0][1] for r in rows],
              'reached', [len(r['paths']) >= 2 for r in rows],
              'median_seconds', round(statistics.median(r['wall_seconds'] for r in rows), 4))


if __name__ == '__main__':
    main()
