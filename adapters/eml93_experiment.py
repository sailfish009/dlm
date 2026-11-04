#!/usr/bin/env python3
"""CPU-only input generation + independent oracle, never the learner/executor.

Native Maru receives numeric observations and abstract source IDs, NOT these
reference functions, names, target expressions, branch corrections or answers to
heldout queries. This is synthetic mechanism validation, not free-text learning.
"""
import argparse
import cmath
import hashlib
import itertools
import json
import math
from pathlib import Path
import random
import subprocess
import time

from sexp import Symbol as S, dumps, loads_many

ROOT = Path(__file__).resolve().parents[1]
SCALE = 1_000_000


def z(value):
    value = complex(value)
    return [S('z93'), round(value.real * SCALE), round(value.imag * SCALE)]


def unz(value):
    if value[0] != 'z93':
        raise AssertionError(value)
    return complex(value[1] / SCALE, value[2] / SCALE)


# Evaluation oracle only. None of these functions is visible to native discovery.
REFERENCES = {
    'u1': lambda x: cmath.exp(x),
    'u2': lambda x: cmath.log(x),
    'u3': lambda x, y: x - y,
    'u4': lambda x, y: cmath.exp(x - y),
}
POINTS = {
    'u1': [(.2,), (.7,), (1.1,), (1.5,), (-.2,), (-.6,), (-1.,)],
    'u2': [(.5,), (.8,), (1.3,), (2.,), (3.,)],
    'u3': [(a, b) for bsign in (1, -1) for a, b in
           [(0.3, .2 * bsign), (.8, .3 * bsign), (1.4, .6 * bsign), (2., .4 * bsign)]],
    'u4': [(a, b) for bsign in (1, -1) for a, b in
           [(.35, .2 * bsign), (.9, .3 * bsign), (1.5, .6 * bsign), (2.1, .4 * bsign)]],
}


def rows(source, points=None):
    points = POINTS[source] if points is None else points
    return [[S('row93'), S(f'r{i}'), [z(x) for x in point],
             z(REFERENCES[source](*[unz(z(x)) for x in point]))]
            for i, point in enumerate(points)]


def curriculum(seed=0, negative_log=False):
    rng = random.Random(seed)
    commands = []
    for source, points in POINTS.items():
        observed = rows(source)
        rng.shuffle(observed)
        commands += [[S('observe93'), S(source), len(points[0]), observed],
                     [S('learn93'), S(source), 3, 200000]]
    if negative_log:
        commands.append([S('observe93'), S('u2'), 1,
                         rows('u2', POINTS['u2'] + [(-.5,), (-1.2,), (-2.5,)])])
    return commands


def heldout(seed=0, count=16, negative_log=False):
    rng = random.Random(seed + 9103)
    queries, expected = [], []
    for source in REFERENCES:
        for i in range(count):
            if source == 'u1':
                point = (rng.uniform(-1.2, -.05) if i % 2 else rng.uniform(.1, 1.8),)
            elif source == 'u2':
                point = (-rng.uniform(.45, 3.5) if negative_log and i % 2 else rng.uniform(.45, 3.5),)
            else:
                point = (rng.uniform(.25, 2.3), rng.uniform(.1, .8) * (-1 if i % 2 else 1))
            inputs = [z(x) for x in point]
            queries.append([S('query93'), S(source), inputs, 200000])
            expected.append(REFERENCES[source](*map(unz, inputs)))
    return queries, expected


def fixture(branch='lower93', seed=0, negative_log=False, count=16):
    queries, expected = heldout(seed, count, negative_log)
    return [S('eml-input93'), 1, S(branch), curriculum(seed, negative_log), queries], expected


def native(data):
    started = time.perf_counter()
    child = subprocess.run([str(ROOT / 'scripts/run.sh'), 'eml93-input'], input=dumps(data),
                           text=True, capture_output=True, timeout=180)
    if child.returncode:
        raise AssertionError(child.stderr[-4000:] + child.stdout[-1000:])
    return loads_many(child.stdout), time.perf_counter() - started


def evaluate(seed, branch, negative_log):
    data, expected = fixture(branch, seed, negative_log)
    output, seconds = native(data)
    transitions = [v for v in output if v[0] == 'transition93']
    core = next(v[1] for v in output if v[0] == 'frozen93')
    answers = [v for v in output if v[0] == 'answer93']
    assert len(answers) == len(expected)
    complete = unknown = mismatches = 0
    errors = []
    by_source = {}
    for query, answer, target in zip(data[4], answers, expected):
        source = str(query[1])
        by_source.setdefault(source, {'complete': 0, 'unknown': 0, 'mismatches': 0})
        if answer[1] != 'complete':
            unknown += 1
            by_source[source]['unknown'] += 1
            continue
        complete += 1
        by_source[source]['complete'] += 1
        error = abs(unz(answer[2]) - target)
        errors.append(error)
        if error > .002:
            mismatches += 1
            by_source[source]['mismatches'] += 1
    return {'seed': seed, 'branch': branch, 'negative_log_observed': negative_log,
            'seconds_including_startup': seconds, 'core': core,
            'basis_count': len(core[3]), 'active_scope_count': len(core[4]),
            'complete': complete, 'unknown': unknown, 'mismatches': mismatches,
            'max_absolute_error': max(errors, default=0), 'by_source': by_source,
            'transitions': transitions,
            'input_sha256': hashlib.sha256(dumps(data).encode()).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--write-fixture', action='store_true')
    parser.add_argument('--seeds', type=int, default=3)
    args = parser.parse_args()
    if args.write_fixture:
        data, _ = fixture(count=4)
        (ROOT / 'experiments/eml93/input-example.sexp').write_text(dumps(data) + '\n')
        return
    runs = [evaluate(seed, branch, negative)
            for seed, branch, negative in itertools.product(range(args.seeds),
                                                            ('principal93', 'lower93'), (False, True))]
    result = {'scope': 'Synthetic EML-based native structure formation; not end-to-end web semantics, not formal world-law induction or exact arithmetic.',
              'backend': 'Maru native complex fixed-point 1e-6; Python cmath independent oracle',
              'tolerance_absolute': .002, 'runs': runs,
              'total_complete_checks': sum(r['complete'] for r in runs),
              'total_unknown': sum(r['unknown'] for r in runs),
              'total_mismatches': sum(r['mismatches'] for r in runs)}
    text = json.dumps(result, indent=2) + '\n'
    if args.output:
        args.output.write_text(text)
    else:
        print(text, end='')
    if result['total_mismatches']:
        raise SystemExit('oracle mismatch')


if __name__ == '__main__':
    main()
