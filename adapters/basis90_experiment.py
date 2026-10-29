#!/usr/bin/env python3
"""CPU/offline development measurement and independent relational oracle.

Not a runtime learner. Native Maru discovers, selects, checks and executes bases.
All arms pay the same two discovery phases; timings are exploratory fresh-process
end-to-end measurements, not isolated inference speedups. No network/dependencies.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import statistics
import subprocess
import tempfile
import time

from sexp import Symbol as S, dumps, loads_many

ROOT = Path(__file__).resolve().parents[1]


def rel(name):
    return [S('rel90'), S(name)]


def join(a, b):
    return [S('join90'), a, b]


def expression(word):
    value = rel(word[0])
    for p in word[1:]:
        value = join(value, rel(p))
    return value


def reference(word, facts):
    relations = {p: {tuple(f[2]) for f in facts if f[1] == p} for p in word}
    pairs = relations[word[0]]
    for p in word[1:]:
        pairs = {(a, d) for a, b in pairs for c, d in relations[p] if b == c}
    return pairs


def workloads():
    # Names and words define tasks, not desired discovered bases or answer labels.
    return {
        'recursive': ([('q1', 'rst'), ('q2', 'rsu'), ('q3', 'vrs')],
                      [('q4', 'rstu'), ('q5', 'vrst')]),
        'no-repeat': ([('q1', 'rs'), ('q2', 'tu'), ('q3', 'vr')], []),
        'small-overhead': ([('q1', 'rs'), ('q2', 'rs')], []),
        'overlap': ([('q1', 'rst'), ('q2', 'rsu'), ('q3', 'str'), ('q4', 'stu')],
                    [('q5', 'rstu')]),
    }


def run_experiment(repeats=2, query_batches=3):
    configurations = [(name, seed, arm, repeat) for name in workloads()
                      for seed in (90, 91, 92) for arm in ('raw', 'append', 'basis', 'memo')
                      for repeat in range(repeats)]
    random.Random(90).shuffle(configurations)
    records = []
    for name, seed, arm, repeat in configurations:
        rng = random.Random(seed)
        facts = [[S('atom'), S(p), [S(a), S(b)]]
                 for p in 'rstuv' for a in 'abcd' for b in 'abcd' if rng.random() < .2]
        # Keep the native capacity explicit, never select by whether queries solve.
        facts = facts[:24]
        first, following = workloads()[name]
        request = [S('basis-measure90'), 1, list(map(S, 'rstuv')), facts,
                   [[S(k), expression(w)] for k, w in first],
                   [[S(k), expression(w)] for k, w in following], S(arm), query_batches]
        payload = dumps(request) + '\n'
        start = time.perf_counter()
        with tempfile.TemporaryFile() as source, tempfile.TemporaryFile() as output, tempfile.TemporaryFile() as errors:
            source.write(payload.encode())
            source.seek(0)
            proc = subprocess.Popen([str(ROOT / 'scripts/run.sh'), 'proof',
                                     str(ROOT / 'experiments/basis90/measure.l')],
                                    stdin=source, stdout=output, stderr=errors)
            # One child at a time: per-child CPU/RSS, without pipe deadlocks.
            _, status, usage = os.wait4(proc.pid, 0)
            proc.returncode = os.waitstatus_to_exitcode(status)
            output.seek(0)
            errors.seek(0)
            stdout, stderr = output.read(), errors.read()
        elapsed = time.perf_counter() - start
        if proc.returncode:
            raise RuntimeError(stderr.decode(errors='replace')[-4000:])
        row, = loads_many(stdout.decode())
        if row[0] != 'measurement90' or row[3][1] != 'complete':
            raise ValueError('invalid/incomplete native measurement')
        actual = {str(a[1]): set(map(tuple, a[2])) for a in row[3][2]}
        expected = {key: reference(word, facts) for key, word in first + following}
        if actual != expected:
            raise AssertionError((name, seed, arm, actual, expected))
        core, audit, result = row[1:]
        records.append(dict(workload=name, seed=seed, arm=arm, repeat=repeat,
                            query_batches=query_batches, wall_seconds=elapsed,
                            user_seconds=usage.ru_utime, system_seconds=usage.ru_stime,
                            max_rss_kib=usage.ru_maxrss,
                            request_sha256=hashlib.sha256(payload.encode()).hexdigest(),
                            execution_core_bytes=len(dumps(core).encode()),
                            audit_bytes=len(dumps(audit).encode()),
                            native_output_bytes=len(stdout), basis_count=len(core[3]),
                            work_nodes=sum(nodes(t[3]) for t in core[4]),
                            basis_body_nodes=sum(nodes(m[2]) for m in core[3]),
                            metrics_last_batch=result[3], oracle_queries=len(expected), mismatches=0))
    groups = {}
    for name in workloads():
        groups[name] = {}
        for arm in ('raw', 'append', 'basis', 'memo'):
            rows = [r for r in records if r['workload'] == name and r['arm'] == arm]
            groups[name][arm] = {key: statistics.median(r[key] for r in rows)
                                 for key in ('wall_seconds', 'user_seconds', 'system_seconds',
                                             'max_rss_kib', 'execution_core_bytes', 'audit_bytes',
                                             'work_nodes', 'basis_body_nodes')}
    return dict(experiment='basis90-v1', cpu_only=True, network=False,
                selection='fixed workload names, seeds, capacity cap; no answer filtering',
                controls={'raw': 'original programs; no basis in execution core',
                          'append': 'same learned basis available, original programs unchanged',
                          'basis': 'learned basis with rewritten execution plans',
                          'memo': 'original relations with canonical expression memoization'},
                accounting='All processes include startup, input, both discovery phases, checking, '
                           'query batches and output. No attached checkpoint; core/audit bytes use '
                           'Python canonical S-expression encoding. Per-batch cache is cold at each '
                           'batch. append is an experiment control, not the legacy a77 benchmark. '
                           'Measurement views are not independently restorable snapshots.',
                summaries=groups, records=records)


def nodes(e):
    return 1 + nodes(e[1]) + nodes(e[2]) if e[0] == 'join90' else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--repeats', type=int, default=2)
    parser.add_argument('--query-batches', type=int, default=3)
    args = parser.parse_args()
    if not 1 <= args.repeats <= 5 or not 1 <= args.query_batches <= 20:
        parser.error('repeats 1..5; query-batches 1..20')
    result = run_experiment(args.repeats, args.query_batches)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'runs': len(result['records']),
                      'mismatches': sum(r['mismatches'] for r in result['records']),
                      'output': str(args.output)}))


if __name__ == '__main__':
    main()
