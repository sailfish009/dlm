#!/usr/bin/env python3
"""CPU/offline developer experiment: native interpretation/formation vs controls.
No Python policy or runtime learner. All answers/witnesses checked by finite
assignment enumeration, not by native joins. Timings include startup and all
training/validation; no attached checkpoint in this measurement.
"""
import argparse
import hashlib
import itertools
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


def workloads():
    return {
        'chain': [('r', 'a', 'b'), ('s', 'b', 'c'), ('t', 'c', 'd'),
                  ('r', 'p', 'q'), ('s', 'q', 'z'), ('t', 'z', 'w')],
        'fork-overhead': [('r', 'a', 'b'), ('s', 'a', 'c'), ('r', 'p', 'q'), ('s', 'p', 'z')],
        'ambiguous': [('r', 'a', 'b'), ('s', 'b', 'c'), ('s', 'a', 'd'),
                      ('s', 'e', 'b'), ('r', 'e', 'd'), ('t', 'c', 'd')],
        'no-repeat': [('r', 'a', 'b'), ('s', 'b', 'c'), ('t', 'e', 'f')],
    }


def facts_for(name, seed):
    triples = list(workloads()[name])
    rng = random.Random(seed)
    rng.shuffle(triples)  # deliberate candidate tie/order sensitivity is retained
    train = [[S('atom'), S(p), [S(f'train{seed}-{a}'), S(f'train{seed}-{b}')]] for p, a, b in triples]
    kept = [f for f in triples if rng.random() < .8]
    if not kept:
        kept = triples[:1]
    test = [[S('atom'), S(p), [S(f'heldout{seed}-{a}'), S(f'heldout{seed}-{b}')]] for p, a, b in kept]
    return train, test


def reference(pattern, facts):
    nodes = sorted({x for f in facts for x in f[2]}, key=str)
    relation = {(f[1], *f[2]) for f in facts}
    arity = 1 + max(v for a in pattern for v in a[1:])
    return {values for values in itertools.product(nodes, repeat=arity)
            if all((pred, values[a], values[b]) in relation for pred, a, b in pattern)}


def check_rows(pattern, rows, facts):
    actual = set()
    for tag, values, ids in rows:
        if tag != 'match91' or len(values) != 1 + max(v for a in pattern for v in a[1:]) or len(ids) != len(pattern):
            raise AssertionError((pattern, rows))
        for (pred, a, b), i in zip(pattern, ids):
            if not isinstance(i, int) or not 0 <= i < len(facts) or facts[i] != [S('atom'), pred, [values[a], values[b]]]:
                raise AssertionError(('invalid witness', pattern, values, ids))
        actual.add(tuple(values))
    if len(actual) != len(rows) or actual != reference(pattern, facts):
        raise AssertionError(('answer mismatch', pattern, rows, facts))


def run_experiment(repeats=2, batches=3, seeds=(91, 92, 93)):
    configs = [(name, seed, arm, repeat) for name in workloads() for seed in seeds
               for arm in ('raw', 'memo', 'append', 'basis') for repeat in range(repeats)]
    random.Random(91).shuffle(configs)
    records = []
    for name, seed, arm, repeat in configs:
        train, test = facts_for(name, seed)
        request = [S('basis-measure91'), 1, list(map(S, 'rst')), train, test, 2, S(arm), batches]
        payload = (dumps(request) + '\n').encode()
        start = time.perf_counter()
        with tempfile.TemporaryFile() as source, tempfile.TemporaryFile() as output, tempfile.TemporaryFile() as errors:
            source.write(payload)
            source.seek(0)
            proc = subprocess.Popen([str(ROOT / 'scripts/run.sh'), 'proof', str(ROOT / 'experiments/basis91/measure.l')],
                                    stdin=source, stdout=output, stderr=errors)
            _, status, usage = os.wait4(proc.pid, 0)
            proc.returncode = os.waitstatus_to_exitcode(status)
            output.seek(0)
            errors.seek(0)
            stdout, stderr = output.read(), errors.read()
        elapsed = time.perf_counter() - start
        if proc.returncode:
            raise RuntimeError(stderr.decode(errors='replace')[-4000:])
        row, = loads_many(stdout.decode())
        if len(row) != 6 or row[0] != 'measurement91' or row[4][0] != 'batch91' or row[4][1] != 'complete':
            raise AssertionError(row)
        model, evidence, audit, batch, probes = row[1:]
        for tag, pattern, answers in batch[2]:
            if tag != 'answer91':
                raise AssertionError(tag)
            check_rows(pattern, answers, train)
        profiles = []
        for probe in probes:
            if probe[0] != 'execution91' or probe[1] != 'complete':
                raise AssertionError(probe)
            check_rows(probe[2], probe[3], test)
            profiles.append(dict(pattern=probe[2], matches=len(probe[3]), metrics=probe[4]))
        records.append(dict(workload=name, seed=seed, arm=arm, repeat=repeat, batches=batches,
                            wall_seconds=elapsed, user_seconds=usage.ru_utime, system_seconds=usage.ru_stime,
                            max_rss_kib=usage.ru_maxrss,
                            request_sha256=hashlib.sha256(payload).hexdigest(),
                            native_output_sha256=hashlib.sha256(stdout).hexdigest(),
                            model_bytes=len(dumps(model).encode()), evidence_bytes=len(dumps(evidence).encode()),
                            audit_bytes=len(dumps(audit).encode()), native_output_bytes=len(stdout),
                            reading_count=len(model[4]), basis_count=len(model[3]),
                            active_ops=sum(len(v[4]) for v in model[4]),
                            basis_body_ops=sum(len(m[3]) for m in model[3]),
                            metrics_last_batch=batch[3], heldout_profiles=profiles,
                            oracle_queries=len(batch[2]) + len(probes), mismatches=0))
    summaries = {}
    for name in workloads():
        summaries[name] = {}
        for arm in ('raw', 'memo', 'append', 'basis'):
            rows = [r for r in records if r['workload'] == name and r['arm'] == arm]
            summaries[name][arm] = {k: statistics.median(r[k] for r in rows)
                                   for k in ('wall_seconds', 'user_seconds', 'system_seconds', 'max_rss_kib',
                                             'model_bytes', 'evidence_bytes', 'audit_bytes', 'active_ops',
                                             'basis_body_ops', 'reading_count', 'basis_count')}
    return dict(experiment='basis91-v1', cpu_only=True, network=False,
                selection='Fixed workloads and seeds, no filtering by learned basis or answer success. '
                          'Seeds shuffle training fact order/rename constants and perturb heldout graphs.',
                accounting='All arms pay the same data interpretation and up to two formation phases. '
                           'Cold cache per batch/probe. Startup, checking, queries and serialization included; '
                           'attached-checkpoint costs excluded. Model excludes answer rows; evidence/audit '
                           'reported separately using Python canonical S-expression bytes. Measurement cores '
                           'are nonpersistent views, not replay-valid saved sessions. No trained latent space '
                           'or general speedup claim. Child RSS includes launch/startup.',
                summaries=summaries, records=records)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', required=True, type=Path)
    p.add_argument('--repeats', type=int, default=2)
    p.add_argument('--batches', type=int, default=3)
    args = p.parse_args()
    if not 1 <= args.repeats <= 5 or not 1 <= args.batches <= 8:
        p.error('repeats 1..5; batches 1..8')
    result = run_experiment(args.repeats, args.batches)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(runs=len(result['records']),
                          oracle_queries=sum(r['oracle_queries'] for r in result['records']),
                          mismatches=sum(r['mismatches'] for r in result['records']), output=str(args.output))))


if __name__ == '__main__':
    main()
