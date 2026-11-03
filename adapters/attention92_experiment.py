#!/usr/bin/env python3
"""CPU/offline experiment. Python supplies fixed data and an independent oracle,
never a selection policy. Timings include startup/formation/index/checking/output;
checkpoint/replay costs are separate tests. Controlled queries have fresh indexes;
predecessor complete-result caches are shared within each episode/batch.
"""
import argparse
from functools import lru_cache
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
ARMS = ('raw', 'memo', 'basis', 'ordered92', 'indexed92', 'adaptive92', 'narrow92')
PATTERNS = [[list(map(lambda x: S(x) if isinstance(x, str) else x, a)) for a in atoms] for atoms in [
    [('r', 0, 1), ('s', 1, 2), ('t', 2, 3)],
    [('r', 0, 1), ('s', 1, 2)], [('r', 0, 1), ('s', 0, 2)],
    [('r', 0, 1), ('s', 2, 1)], [('r', 0, 1), ('s', 1, 0)],
    [('r', 0, 0)], [('r', 0, 1), ('s', 1, 2), ('r', 2, 3)],
    [('t', 2, 3), ('s', 1, 2), ('r', 0, 1)]]]
CHAIN = [('r', 'a', 'b'), ('s', 'b', 'c'), ('t', 'c', 'd'),
         ('r', 'p', 'q'), ('s', 'q', 'z'), ('t', 'z', 'w')]
DENSE = [('r', 'a', 'b'), ('r', 'c', 'd'), ('r', 'e', 'f'), ('r', 'g', 'h'),
         ('s', 'b', 'c'), ('s', 'd', 'e'), ('s', 'f', 'g'), ('t', 'c', 'd')]


def workloads():
    return {
        'chain': (CHAIN, CHAIN),
        'selective-tail': (CHAIN, DENSE),
        'fork': ([('r', 'a', 'b'), ('s', 'a', 'c'), ('r', 'p', 'q'), ('s', 'p', 'z')],
                 [('r', 'a', 'b'), ('s', 'a', 'c'), ('t', 'c', 'd'), ('r', 'e', 'b'), ('s', 'e', 'c')]),
        'ambiguous': ([('r', 'a', 'b'), ('s', 'b', 'c'), ('s', 'a', 'd'),
                       ('s', 'e', 'b'), ('r', 'e', 'd'), ('t', 'c', 'd')],
                      [('r', 'a', 'b'), ('s', 'b', 'c'), ('s', 'a', 'd'),
                       ('s', 'e', 'b'), ('r', 'e', 'd'), ('t', 'c', 'd')]),
        'no-repeat': ([('r', 'a', 'b'), ('s', 'b', 'c'), ('t', 'e', 'f')],
                      [('r', 'a', 'b'), ('s', 'd', 'c'), ('t', 'e', 'f')])}


def facts_for(name, seed):
    rng = random.Random(seed)
    result = []
    for label, triples in zip(('train', 'heldout'), workloads()[name]):
        triples = list(triples)
        rng.shuffle(triples)
        # Pure name/order perturbation, not independent unseen task distributions.
        result.append([[S('atom'), S(p), [S(f'{label}{seed}-{a}'), S(f'{label}{seed}-{b}')]] for p, a, b in triples])
    return tuple(result)


@lru_cache(maxsize=512)
def reference(pattern_text, facts_text):
    pattern, = loads_many(pattern_text)
    facts, = loads_many(facts_text)
    nodes = sorted({v for f in facts for v in f[2]}, key=str)
    available = {(f[1], *f[2]) for f in facts}
    arity = 1 + max(v for a in pattern for v in a[1:])
    return {values for values in itertools.product(nodes, repeat=arity)
            if all((p, values[x], values[y]) in available for p, x, y in pattern)}


def check_rows(pattern, rows, facts):
    actual = set()
    for tag, values, ids in rows:
        if tag != 'match91' or len(ids) != len(pattern) or len(values) != 1 + max(v for a in pattern for v in a[1:]):
            raise AssertionError((pattern, rows))
        for (p, a, b), i in zip(pattern, ids):
            if type(i) is not int or not 0 <= i < len(facts) or facts[i] != [S('atom'), p, [values[a], values[b]]]:
                raise AssertionError(('witness mismatch', pattern, values, ids))
        actual.add(tuple(values))
    if len(actual) != len(rows) or actual != reference(dumps(pattern), dumps(facts)):
        raise AssertionError(('answer mismatch', pattern, rows, facts))


def run_experiment(repeats=2, batches=2, seeds=(92, 93, 94), cases=None):
    names = tuple(cases) if cases is not None else tuple(workloads())
    configs = [(name, seed, arm, repeat) for name in names for seed in seeds for arm in ARMS for repeat in range(repeats)]
    random.Random(92).shuffle(configs)
    records = []
    for name, seed, arm, repeat in configs:
        train, heldout = facts_for(name, seed)
        request = [S('attention-measure92'), 1, list(map(S, 'rst')), train, heldout, PATTERNS, 2, S(arm), batches]
        payload = (dumps(request) + '\n').encode()
        start = time.perf_counter()
        with tempfile.TemporaryFile() as source, tempfile.TemporaryFile() as output, tempfile.TemporaryFile() as errors:
            source.write(payload); source.seek(0)
            proc = subprocess.Popen([str(ROOT / 'scripts/run.sh'), 'proof', str(ROOT / 'experiments/attention92/measure.l')],
                                    stdin=source, stdout=output, stderr=errors)
            _, status, usage = os.wait4(proc.pid, 0)
            proc.returncode = os.waitstatus_to_exitcode(status)
            output.seek(0); errors.seek(0)
            stdout, stderr = output.read(), errors.read()
        elapsed = time.perf_counter() - start
        if proc.returncode:
            raise RuntimeError(stderr.decode(errors='replace')[-4000:])
        row, = loads_many(stdout.decode())
        if len(row) != 6 or row[0] != 'measurement92':
            raise AssertionError(row)
        model, evidence, audit, answers, profiles = row[1:]
        if len(answers) != len(PATTERNS) * 2:
            raise AssertionError('missing answers')
        checks = []
        for (episode, result), expected_pattern in zip(answers, PATTERNS * 2):
            if result[0] not in ('execution91', 'attention-result92') or result[1] != 'complete' or result[2] != expected_pattern:
                raise AssertionError(result)
            facts = train if episode == 'train' else heldout
            check_rows(result[2], result[3], facts)
            checks.append(dict(episode=str(episode), pattern=result[2], matches=len(result[3]),
                               metrics=result[4], plan=result[5] if len(result) > 5 else None,
                               trace_bytes=len(dumps(result[6]).encode()) if len(result) > 6 else 0))
        records.append(dict(workload=name, seed=seed, arm=arm, repeat=repeat, batches=batches,
                            wall_seconds=elapsed, user_seconds=usage.ru_utime, system_seconds=usage.ru_stime,
                            max_rss_kib=usage.ru_maxrss,
                            request_sha256=hashlib.sha256(payload).hexdigest(), native_output_sha256=hashlib.sha256(stdout).hexdigest(),
                            model_bytes=len(dumps(model).encode()), evidence_bytes=len(dumps(evidence).encode()),
                            audit_bytes=len(dumps(audit).encode()), output_bytes=len(stdout),
                            peak_serialized_control_bytes=max((len(dumps(p).encode()) for p in profiles), default=0),
                            basis_count=len(model[3]), profiles=checks, oracle_queries=len(checks), mismatches=0))
    summaries = {}
    for name in names:
        summaries[name] = {}
        for arm in ARMS:
            rows = [r for r in records if r['workload'] == name and r['arm'] == arm]
            summaries[name][arm] = {key: statistics.median(r[key] for r in rows) for key in
                                   ('wall_seconds', 'user_seconds', 'system_seconds', 'max_rss_kib', 'model_bytes',
                                    'evidence_bytes', 'audit_bytes', 'output_bytes', 'peak_serialized_control_bytes', 'basis_count')}
    return dict(experiment='attention92-v1', cpu_only=True, network=False,
                selection='Fixed cases, seeds and queries, no filtering for learned bases or success. '
                          'Seeds shuffle facts and rename nodes, not independent distributions. '
                          'narrow92 deliberately truncates focus as a failure/fallback stress policy.',
                accounting='All arms pay the same native formation and retain the same frozen executable core. '
                           'Raw/memo/basis are predecessor executors with complete full-source caches shared within each immutable episode/batch; memo also caches structural plans. Ordered/indexed/adaptive/narrow share the new scoped backend and checker, with a fresh context/index per query and no partial result cache. '
                           'New local admission includes an independent full-source predecessor replay, charged as checker units. '
                           'All timings include startup, formation, indexes, selection, verification, repeated queries and output; '
                           'no attached checkpoint. Only final-batch answers serialized and oracle checked; repetitions are not additional independent oracle cases. '
                           'Core excludes training answer rows. Control bytes describe peak serialized per-query index/work/events, '
                           'not heap use or learned model parameters. Metrics91/92 have different units; do not compare their totals directly. '
                           'Logical fuel is not a wall-time bound: allocation, list walks, model preflight and inspection are not fully charged.',
                summaries=summaries, records=records)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--repeats', type=int, default=2)
    p.add_argument('--batches', type=int, default=2)
    args = p.parse_args()
    if not 1 <= args.repeats <= 5 or not 1 <= args.batches <= 8:
        p.error('repeats 1..5, batches 1..8')
    result = run_experiment(args.repeats, args.batches)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(runs=len(result['records']), oracle_queries=sum(r['oracle_queries'] for r in result['records']),
                          mismatches=sum(r['mismatches'] for r in result['records']), output=str(args.output))))


if __name__ == '__main__':
    main()
