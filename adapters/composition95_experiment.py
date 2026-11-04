#!/usr/bin/env python3
"""CPU native experiment adapter: data generation and independent math oracle.
No learner, semantic extraction, fitted target templates, or model runtime here.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import resource
import subprocess
import time
from sexp import Symbol as S, dumps, loads_many

ROOT = Path(__file__).resolve().parents[1]

def z(x):
    return [S('z93'), round(float(x) * 1_000_000), 0]

def frame(name, u, v, seed=0, reverse=False):
    """A given observation schema, NOT discovered free-text semantics.
    Shared middle object creates nine relation matches from six source facts.
    Six independent external target observations supervise typed construction.
    """
    a = [f'{name}-a{i}' for i in range(3)]
    c = [f'{name}-c{i}' for i in range(3)]
    b = f'{name}-b'
    facts = [[S('atom'), S('r'), [x, b]] for x in a]
    facts += [[S('atom'), S('s'), [b, x]] for x in c]
    measures = [[S('measure95'), obj, z(val)] for obj, val in zip(a + [b] + c, list(u) + [0.7351] + list(v))]
    targets = []
    for k, (i, j) in enumerate([(0, 0), (0, 1), (1, 1), (1, 2), (2, 0), (2, 2)]):
        val = float(u[i]) - float(v[j])
        if reverse:
            val = math.exp(val)
        targets.append([S('observed95'), f'{name}-t{k}', [a[i], b, c[j]], z(val)])
    rng = random.Random(seed)
    rng.shuffle(facts)
    rng.shuffle(measures)
    rng.shuffle(targets)
    return [S('frame95'), name, f'{name}-episode', facts, measures, targets]

def fixture(seed=0, branch='principal93', arm='shared95', nqueries=4):
    train = [[S('atom'), S('r'), ['a', 'b']], [S('atom'), S('s'), ['b', 'c']],
             [S('atom'), S('r'), ['d', 'e']], [S('atom'), S('s'), ['e', 'f']]]
    random.Random(seed).shuffle(train)
    calibrations = []
    for name, fun, inputs in [('nalpha', math.exp, [0.21, 0.57, 0.94, 1.32]),
                              ('nbeta', math.log, [0.31, 0.67, 1.17, 1.83])]:
        rows = [[S('row93'), f'{name}-{i}', [z(x)], z(fun(x))] for i, x in enumerate(inputs)]
        random.Random(seed + 5).shuffle(rows)
        calibrations.append([S('calibration-input95'), name, 1, rows])
    fc = frame(f'channel-c-{seed}', [1.25, 1.93, 2.61], [.17, .46, .83], seed)
    fd = frame(f'channel-d-{seed}', [1.33, 2.02, 2.81], [.14, .51, .93], seed + 1, True)
    queries = []
    rng = random.Random(101 + seed)
    for i in range(nqueries):
        uf = [round(rng.uniform(1.1, 2.7), 4) for _ in range(3)]
        vf = [round(rng.uniform(.15, .95), 4) for _ in range(3)]
        fr = frame(f'q-{seed}-{i}', uf, vf, seed + i)
        ctx = [S('context95'), f'q-{seed}-{i}', 1, fr[3], fr[4]]
        for ch in (fc[1], fd[1]):
            queries.append([S('typed-query95'), ch, ctx])
    return [S('composition-input95'), 1, [S('r'), S('s')], train, calibrations, fc, fd,
            queries, S(arm), S(branch), 3, 200000]

def oracle(context, transformed):
    values = {m[1]: complex(m[2][1] / 1e6, m[2][2] / 1e6) for m in context[4]}
    out = {}
    for i, f in enumerate(context[3]):
        if f[1] != 'r':
            continue
        for j, g in enumerate(context[3]):
            if g[1] != 's' or f[2][1] != g[2][0]:
                continue
            tup = (f[2][0], f[2][1], g[2][1])
            d = values[tup[0]] - values[tup[2]]
            out[tup] = (complex(math.exp(d.real), 0) if transformed else d, [i, j])
    return out

def run(data):
    start = time.perf_counter()
    p = subprocess.run([str(ROOT / 'scripts/run.sh'), 'compose95-input'], input=dumps(data) + '\n',
                       text=True, capture_output=True, cwd=ROOT, timeout=180)
    elapsed = time.perf_counter() - start
    if p.returncode or 'ERROR:' in p.stdout + p.stderr or 'FATAL:' in p.stdout + p.stderr:
        raise RuntimeError((p.stdout + p.stderr)[-6000:])
    records = loads_many(p.stdout)
    model = next(r[1] for r in records if r[0] == 'standalone-model95')
    outcomes = [r for r in records if r[0] == 'query-result95']
    assert len(outcomes) == len(data[7])
    count = {'complete': 0, 'unknown': 0, 'checked_rows': 0, 'mismatches': 0}
    max_error = 0.0
    for rec, q in zip(outcomes, data[7]):
        answer = rec[3]
        assert rec[1:3] == [q[1], q[2][1]]
        if answer[1] == 'unknown':
            assert answer[3] == []
            count['unknown'] += 1
            continue
        assert answer[:3] == ['typed-answer95', 'complete', 'empirical95'], answer
        expected = oracle(q[2], q[1] == data[6][1])
        got = {tuple(r[1]): r for r in answer[3]}
        assert len(got) == len(answer[3])
        if set(got) != set(expected):
            count['mismatches'] += 1
        for tup, row in got.items():
            value = complex(row[2][1] / 1e6, row[2][2] / 1e6)
            err = abs(value - expected[tup][0])
            max_error = max(max_error, err)
            if err > .002 or row[3][3] != expected[tup][1]:
                count['mismatches'] += 1
            count['checked_rows'] += 1
        count['complete'] += 1
    checks = next(r for r in records if r[0] == 'checks95')
    assert all(checks[1:]), checks
    return {'arm': str(data[8]), 'branch': str(data[9]), 'input_sha256': hashlib.sha256(dumps(data).encode()).hexdigest(),
            'data_sha256': hashlib.sha256(dumps(data[2:8]).encode()).hexdigest(), 'elapsed_seconds': elapsed,
            'model_json_bytes': len(json.dumps(model, separators=(',', ':')).encode()), 'library': model[3],
            'profile': next(r[1] for r in records if r[0] == 'profile95'), 'counts': count,
            'max_absolute_error': max_error, 'queries': len(data[7]), 'checks': checks,
            'formation': [r for r in records if r[0] in ('formation-c95', 'formation-d95')],
            'metrics': [r[4] for r in outcomes]}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', type=Path)
    ap.add_argument('--example', type=Path)
    ap.add_argument('--seeds', type=int, default=2)
    ap.add_argument('--queries', type=int, default=6)
    ap.add_argument('--repeats', type=int, default=2)
    args = ap.parse_args()
    if not (1 <= args.seeds <= 10 and 1 <= args.queries <= 128 and 1 <= args.repeats <= 10):
        ap.error('seeds/repeats must be 1..10; queries 1..128')
    if args.example:
        args.example.write_text(dumps(fixture(nqueries=args.queries)) + '\n')
        return
    runs = []
    for seed in range(args.seeds):
        for branch in ('principal93', 'lower93'):
            for arm in ('shared95', 'logical95', 'no-relational95', 'no-numeric95', 'no-output95'):
                for repeat in range(args.repeats):
                    row = run(fixture(seed, branch, arm, args.queries))
                    row['seed'] = seed
                    row['repeat'] = repeat
                    expected = 'unknown' if arm in ('no-relational95', 'no-numeric95') else 'complete'
                    assert row['counts'][expected] == row['queries']
                    assert row['counts']['mismatches'] == 0
                    runs.append(row)
                    print(seed, branch, arm, repeat, row['counts'], round(row['elapsed_seconds'], 3), flush=True)
    report = {'version': '0.0095', 'sequential': True, 'runs': runs,
              'peak_child_rss_kib': resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
              'note': 'Whole-process times; RSS is process high-water, not learned-parameter memory.'}
    if args.output:
        args.output.write_text(json.dumps(report, indent=2) + '\n')

if __name__ == '__main__':
    main()
